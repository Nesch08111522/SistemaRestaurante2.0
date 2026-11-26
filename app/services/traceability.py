"""Canonical, privacy-preserving audit anchors."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import unicodedata
from datetime import datetime, timedelta, timezone
from typing import Any, Protocol


class AnchorStore(Protocol):
    def latest(self, *, tipo_recurso: str, id_recurso: int) -> dict[str, Any] | None: ...
    def enqueue(self, *, tipo_recurso: str, id_recurso: int, hash_canonico: str,
                hash_previo: str | None = None) -> dict[str, Any]: ...
    def pending(self, *, limit: int = 50) -> list[dict[str, Any]]: ...
    def mark(self, id_ancla: int, *, estado: str, hash_transaccion: str | None = None,
             ultimo_error: str | None = None) -> dict[str, Any] | None: ...


def _normalise(value: object) -> str:
    return " ".join(unicodedata.normalize("NFKC", str(value or "")).split())


def _secret() -> bytes:
    secret = (os.getenv("TRACEABILITY_PSEUDONYM_SECRET")
              or os.getenv("ANCHOR_PSEUDONYM_SECRET") or os.getenv("SECRET_KEY", ""))
    if len(secret) < 32:
        raise RuntimeError("El secreto de pseudonimización debe tener al menos 32 caracteres.")
    return secret.encode("utf-8")


def pseudonymize(value: object) -> str:
    return hmac.new(_secret(), str(value).encode("utf-8"), hashlib.sha256).hexdigest()


def canonical_hash(payload: dict[str, Any]) -> str:
    """Hash a canonical JSON representation; callers must omit raw PII."""
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def review_hash(review: dict[str, Any]) -> str:
    return canonical_hash({
        "version": "smartresto.trace.v1", "type": "review",
        "id": int(review["id_resena"]), "restaurant": int(review["id_restaurante"]),
        "author": pseudonymize(review["id_usuario"]), "rating": int(review["calificacion"]),
        "comment_sha256": hashlib.sha256(_normalise(review.get("comentario")).casefold().encode("utf-8")).hexdigest(),
        "revision": str(review.get("actualizado_en") or review.get("creado_en") or ""),
    })


def ai_decision_hash(decision: dict[str, Any]) -> str:
    return canonical_hash({
        "version": "smartresto.trace.v1", "type": "ai_decision",
        "id": int(decision["id_decision"]), "kind": _normalise(decision.get("tipo")),
        "entity": _normalise(decision.get("entidad")), "entity_id": decision.get("id_entidad"),
        "actor": pseudonymize(decision["id_usuario_actor"]),
        "input_hash": str(decision.get("hash_entrada") or ""),
        "model": _normalise(decision.get("modelo")), "state": _normalise(decision.get("estado")),
        "created": str(decision.get("creado_en") or ""),
    })


def enqueue_review(review: dict[str, Any], store: AnchorStore | None = None) -> dict[str, Any]:
    from app.repositories.anclas_trazabilidad import AnclasTrazabilidadRepository
    store = store or AnclasTrazabilidadRepository
    previous = store.latest(tipo_recurso="resena", id_recurso=int(review["id_resena"]))
    digest = review_hash(review)
    return store.enqueue(tipo_recurso="resena", id_recurso=int(review["id_resena"]), hash_canonico=digest,
                         hash_previo=previous["hash_canonico"] if previous and previous["hash_canonico"] != digest else None)


def enqueue_ai_decision(decision: dict[str, Any], store: AnchorStore | None = None) -> dict[str, Any]:
    from app.repositories.anclas_trazabilidad import AnclasTrazabilidadRepository
    store = store or AnclasTrazabilidadRepository
    previous = store.latest(tipo_recurso="decision_ia", id_recurso=int(decision["id_decision"]))
    digest = ai_decision_hash(decision)
    return store.enqueue(tipo_recurso="decision_ia", id_recurso=int(decision["id_decision"]), hash_canonico=digest,
                         hash_previo=previous["hash_canonico"] if previous and previous["hash_canonico"] != digest else None)


def process_pending(store: AnchorStore, *, limit: int = 50, mode: str = "dry_run") -> dict[str, int | str]:
    """Process anchors with the audited `anchor(bytes32)` contract when requested."""
    mode = mode.replace("-", "_").lower()
    if mode == "off":
        return {"mode": "off", "processed": 0}
    if mode not in {"dry_run", "onchain"}:
        raise ValueError("Modo de anclaje inválido.")
    if mode == "onchain":
        return _process_onchain(store, limit=limit)
    rows = store.pending(limit=limit)
    rows = [row for row in rows if row.get("estado", "pendiente") in {"pendiente", "fallido"}]
    publisher = None
    now = datetime.now(timezone.utc)
    for row in rows:
        if mode == "dry_run":
            store.mark(int(row["id_ancla"]), estado="simulado")
            continue
        if row.get("estado") in {"enviado", "timeout"} and row.get("hash_transaccion"):
            receipt = publisher.receipt(row["hash_transaccion"])
            if receipt is None:
                store.mark(int(row["id_ancla"]), estado="timeout", proximo_intento_en=now + timedelta(seconds=_setting("ANCHOR_RECEIPT_POLL_SECONDS", 20)))
            elif int(receipt.get("status", 0)) == 1:
                store.mark(int(row["id_ancla"]), estado="confirmado")
            else:
                store.mark(int(row["id_ancla"]), estado="revertido", ultimo_error="La transacción fue revertida por la red.")
            continue
        try:
            tx_hash, nonce = publisher.submit(row["hash_canonico"])
            store.mark(int(row["id_ancla"]), estado="enviado", hash_transaccion=tx_hash, nonce_transaccion=nonce,
                       enviada_en=now, proximo_intento_en=now + timedelta(seconds=_setting("ANCHOR_RECEIPT_POLL_SECONDS", 20)))
        except Exception as exc:
            store.mark(int(row["id_ancla"]), estado="fallido", ultimo_error=_safe_error(exc),
                       proximo_intento_en=now + timedelta(seconds=_setting("ANCHOR_RETRY_SECONDS", 60)))
    return {"mode": mode, "processed": len(rows)}


def _process_onchain(store, *, limit: int, publisher=None, tipo_recurso=None):
    """Persist the signed transaction before broadcasting; never allocate another nonce while pending."""
    with store.worker_lock():
        rows = (store.pending(limit=limit, tipo_recurso=tipo_recurso)
                if tipo_recurso else store.pending(limit=limit))
        # Prioritize recovery of already signed or submitted transactions.
        rows.sort(key=lambda row: (not bool(row.get("hash_transaccion")), row["id_ancla"]))
        if not rows:
            return {"mode": "onchain", "processed": 0}
        publisher = publisher or OnchainPublisher()
        row = rows[0]
        now = datetime.now(timezone.utc)
        anchor_id = int(row["id_ancla"])
        tx_hash = row.get("hash_transaccion")
        if tx_hash:
            receipt = publisher.receipt(tx_hash)
            if receipt is not None:
                succeeded = int(receipt.get("status", 0)) == 1
                if succeeded and not publisher.is_anchored(row['hash_canonico']):
                    store.mark(anchor_id, estado='fallido', ultimo_error='La transacción no registró la huella en el contrato.')
                else:
                    store.mark(anchor_id, estado="confirmado" if succeeded else "revertido")
                return {"mode": "onchain", "processed": 1}
            raw = row.get("transaccion_firmada")
            if not raw:
                # Legacy submitted transaction: monitor only, never create a replacement.
                store.mark(anchor_id, estado="timeout", proximo_intento_en=now + timedelta(seconds=20))
                return {"mode": "onchain", "processed": 1}
        else:
            raw, tx_hash, nonce = publisher.prepare(row["hash_canonico"])
            # This commits before any network broadcast. Crash recovery uses this exact transaction.
            store.mark(anchor_id, estado="enviado", hash_transaccion=tx_hash,
                       nonce_transaccion=nonce, transaccion_firmada=raw, enviada_en=now)
        try:
            publisher.broadcast(raw)
        except Exception as exc:
            # A network error can mean the transaction was accepted; retain the signed bytes.
            store.mark(anchor_id, estado="timeout", ultimo_error=_safe_error(exc),
                       proximo_intento_en=now + timedelta(seconds=20))
        else:
            store.mark(anchor_id, estado="enviado", proximo_intento_en=now + timedelta(seconds=20))
        return {"mode": "onchain", "processed": 1}


def _setting(name: str, default: int) -> int:
    try: value = int(os.getenv(name, str(default)))
    except ValueError as exc: raise ValueError(f"{name} debe ser un entero.") from exc
    if value < 1: raise ValueError(f"{name} debe ser positivo.")
    return value


def _safe_error(exc: Exception) -> str:
    message = str(exc)
    for name in ("CHAIN_RPC_URL", "ANCHOR_PRIVATE_KEY"):
        if value := os.getenv(name, ""): message = message.replace(value, "[redacted]")
    return f"{type(exc).__name__}: {message}"[:500]


class OnchainPublisher:
    """Minimal EVM publisher; never prints private keys or RPC credentials."""
    ABI = [{"inputs":[{"internalType":"bytes32","name":"hash","type":"bytes32"}],"name":"anchor","outputs":[],"stateMutability":"nonpayable","type":"function"},
           {"inputs":[{"name":"","type":"bytes32"}],"name":"anchoredAt","outputs":[{"name":"","type":"uint64"}],"stateMutability":"view","type":"function"}]
    def __init__(self) -> None:
        rpc, address, key = (os.getenv(name, "").strip() for name in ("CHAIN_RPC_URL", "ANCHOR_CONTRACT", "ANCHOR_PRIVATE_KEY"))
        if not rpc or not address or not key: raise RuntimeError("Modo onchain requiere RPC, contrato y clave privada.")
        try:
            from web3 import Web3
            from web3.exceptions import TransactionNotFound
        except ImportError as exc: raise RuntimeError("Instala web3 para anclaje on-chain.") from exc
        self._not_found = TransactionNotFound; self.web3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": _setting("ANCHOR_RPC_TIMEOUT", 30)}))
        if not self.web3.is_connected(): raise RuntimeError("No se pudo conectar al RPC configurado.")
        self.chain_id = int(self.web3.eth.chain_id); expected = os.getenv("CHAIN_ID", "").strip()
        if expected and int(expected) != self.chain_id: raise RuntimeError("CHAIN_ID no coincide con la red RPC.")
        if os.getenv("ANCHOR_CONTRACT_METHOD", "anchor").strip() != "anchor": raise ValueError("El contrato esperado usa anchor(bytes32).")
        if not self.web3.is_address(address): raise ValueError("ANCHOR_CONTRACT no es una dirección EVM válida.")
        address = self.web3.to_checksum_address(address)
        if not self.web3.eth.get_code(address): raise RuntimeError("ANCHOR_CONTRACT no tiene bytecode en la red configurada.")
        self.account = self.web3.eth.account.from_key(key); self.contract = self.web3.eth.contract(address=address, abi=self.ABI)
        self.next_nonce = int(self.web3.eth.get_transaction_count(self.account.address, "pending"))
    def prepare(self, digest: str) -> tuple[str, str, int]:
        if len(digest) != 64 or any(c not in "0123456789abcdefABCDEF" for c in digest): raise ValueError("Hash canónico inválido.")
        nonce = max(self.next_nonce, int(self.web3.eth.get_transaction_count(self.account.address, "pending")))
        tx = self.contract.functions.anchor(bytes.fromhex(digest)).build_transaction({"from":self.account.address,"nonce":nonce,"chainId":self.chain_id,"gas":_setting("ANCHOR_GAS_LIMIT",150000),"gasPrice":self.web3.eth.gas_price})
        signed = self.account.sign_transaction(tx)
        self.next_nonce = nonce + 1
        return signed.raw_transaction.hex(), signed.hash.hex(), nonce
    def broadcast(self, raw: str):
        return self.web3.eth.send_raw_transaction(bytes.fromhex(raw.removeprefix("0x")))
    def is_anchored(self, digest: str) -> bool:
        return bool(self.contract.functions.anchoredAt(bytes.fromhex(digest.strip())).call())
    def receipt(self, tx_hash: str):
        try: return self.web3.eth.get_transaction_receipt(tx_hash)
        except self._not_found: return None


def register_cli(app) -> None:
    import click

    @app.cli.command("anchor-traceability")
    @click.option("--limit", default=50, type=click.IntRange(1, 500))
    @click.option("--mode", default="dry-run", type=click.Choice(["off", "dry-run", "onchain"], case_sensitive=False))
    def anchor_traceability(limit: int, mode: str) -> None:
        from app.repositories.anclas_trazabilidad import AnclasTrazabilidadRepository
        result = process_pending(AnclasTrazabilidadRepository, limit=limit, mode=mode)
        click.echo(json.dumps(result, sort_keys=True))
