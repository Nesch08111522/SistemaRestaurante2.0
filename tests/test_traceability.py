import os

import pytest

from app.services import traceability


class Store:
    def __init__(self):
        self.rows = []
        self.marked = []

    def latest(self, **_kwargs):
        return self.rows[-1] if self.rows else None

    def enqueue(self, **kwargs):
        row = {"id_ancla": len(self.rows) + 1, **kwargs}
        self.rows.append(row)
        return row

    def pending(self, *, limit):
        return self.rows[:limit]

    def mark(self, id_ancla, **kwargs):
        self.marked.append((id_ancla, kwargs))


@pytest.fixture(autouse=True)
def trace_secret(monkeypatch):
    monkeypatch.setenv("TRACEABILITY_PSEUDONYM_SECRET", "x" * 32)


def review(**changes):
    item = {"id_resena": 3, "id_restaurante": 9, "id_usuario": 21,
            "calificacion": 5, "comentario": " Excelente  café ", "creado_en": "2026-01-01T00:00:00Z"}
    item.update(changes)
    return item


def test_review_hash_is_stable_without_raw_comment_or_user():
    assert traceability.review_hash(review()) == traceability.review_hash(review(comentario="excelente café"))
    assert len(traceability.review_hash(review())) == 64
    assert traceability.pseudonymize(21) != "21"


def test_legacy_anchor_secret_is_supported(monkeypatch):
    monkeypatch.delenv("TRACEABILITY_PSEUDONYM_SECRET", raising=False)
    monkeypatch.setenv("ANCHOR_PSEUDONYM_SECRET", "legacy-secret-" * 3)
    first = traceability.pseudonymize(21)
    monkeypatch.setenv("ANCHOR_PSEUDONYM_SECRET", "another-secret-" * 3)
    assert first != traceability.pseudonymize(21)


def test_enqueue_chains_an_amended_review():
    store = Store()
    first = traceability.enqueue_review(review(), store)
    second = traceability.enqueue_review(review(actualizado_en="2026-01-02T00:00:00Z"), store)
    assert first["hash_previo"] is None
    assert second["hash_previo"] == first["hash_canonico"]


def test_dry_run_never_submits_onchain(monkeypatch):
    def forbidden():
        raise AssertionError("dry-run no debe crear un cliente blockchain")
    monkeypatch.setattr(traceability, "OnchainPublisher", forbidden)
    store = Store()
    traceability.enqueue_ai_decision({"id_decision": 8, "tipo": "recommend", "entidad": "menu",
                                      "id_usuario_actor": 21, "hash_entrada": "a" * 64,
                                      "estado": "ok", "creado_en": "2026-01-01"}, store)
    assert traceability.process_pending(store, mode="dry-run") == {"mode": "dry_run", "processed": 1}
    assert store.marked == [(1, {"estado": "simulado"})]


def test_dry_run_preserves_submitted_anchors():
    store = Store()
    store.rows = [{"id_ancla": 1, "estado": "enviado"}, {"id_ancla": 2, "estado": "pendiente"}]
    assert traceability.process_pending(store, mode="dry_run")["processed"] == 1
    assert store.marked == [(2, {"estado": "simulado"})]


def test_onchain_persists_before_broadcast_and_recovers_same_transaction():
    from contextlib import nullcontext
    events = []
    class TestStore(Store):
        def worker_lock(self): return nullcontext()
        def mark(self, id_ancla, **kwargs):
            events.append(("mark", kwargs))
            self.rows[0].update(kwargs)
    class Publisher:
        def prepare(self, digest): return "abcd", "0x123", 7
        def is_anchored(self, digest): return True
        def broadcast(self, raw):
            events.append(("broadcast", raw))
            raise TimeoutError("respuesta perdida")
        def receipt(self, tx_hash): return {"status": 1}
    store = TestStore()
    store.rows = [{"id_ancla": 1, "estado": "pendiente", "hash_canonico": "a" * 64}]
    traceability._process_onchain(store, limit=10, publisher=Publisher())
    assert events[0][1]["transaccion_firmada"] == "abcd"
    assert events[1] == ("broadcast", "abcd")
    traceability._process_onchain(store, limit=10, publisher=Publisher())
    assert events[-1][1]["estado"] == "confirmado"


def test_successful_receipt_does_not_confirm_missing_hash():
    from contextlib import nullcontext
    class TestStore(Store):
        def worker_lock(self): return nullcontext()
    class Publisher:
        def receipt(self, tx_hash): return {'status': 1}
        def is_anchored(self, digest): return False
    store = TestStore()
    store.rows = [{'id_ancla': 1, 'estado': 'enviado', 'hash_transaccion': '0x123', 'hash_canonico': 'a' * 64}]
    traceability._process_onchain(store, limit=1, publisher=Publisher())
    assert store.marked[0][1]['estado'] == 'fallido'
