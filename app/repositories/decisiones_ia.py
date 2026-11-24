# app/repositories/decisiones_ia.py
"""
Repositorio de public.decisiones_ia y su tabla hija decisiones_ia_atributos.

Columnas del .sql (decisiones_ia):
  id_decision (identity), tipo, entidad, id_entidad, id_usuario_actor,
  hash_entrada (64 hex), modelo, confianza, decision_final_administrador,
  aceptada, latencia_ms, estado, codigo_error, creado_en

Columnas de decisiones_ia_atributos:
  id_decision, origen ∈ {'entrada','salida'}, ruta, tipo_valor,
  valor_texto, valor_numero, valor_booleano
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


_ESTADOS = frozenset({"reserved", "ok", "error", "cache", "rate_limited", "unavailable"})
_ORIGENES = frozenset({"entrada", "salida"})
_TIPOS_VALOR = frozenset({"texto", "numero", "booleano", "nulo"})
_HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")


class DecisionesIARepository(PostgresRepository):
    table = "public.decisiones_ia"
    columns = frozenset({
        "id_decision", "tipo", "entidad", "id_entidad", "id_usuario_actor",
        "hash_entrada", "modelo", "confianza",
        "decision_final_administrador", "aceptada", "latencia_ms",
        "estado", "codigo_error", "creado_en",
    })

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_decision=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def list_by_actor(
        cls, id_usuario_actor: int, *, limit: int = 100
    ) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_usuario_actor=%s "
                f"ORDER BY creado_en DESC LIMIT %s",
                (int(id_usuario_actor), int(limit)),
            )
            return list(cur.fetchall())

    @classmethod
    def list_by_entidad(
        cls, entidad: str, id_entidad: int, *, limit: int = 100
    ) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} "
                f"WHERE entidad=%s AND id_entidad=%s "
                f"ORDER BY creado_en DESC LIMIT %s",
                (entidad.strip(), int(id_entidad), int(limit)),
            )
            return list(cur.fetchall())

    @classmethod
    def insert(
        cls,
        *,
        tipo: str,
        entidad: str,
        id_usuario_actor: int,
        hash_entrada: str,
        id_entidad: int | None = None,
        modelo: str | None = None,
        confianza: float | None = None,
        estado: str = "reserved",
        latencia_ms: int = 0,
        codigo_error: str | None = None,
        decision_final_administrador: str | None = None,
        aceptada: bool | None = None,
    ) -> dict[str, Any]:
        if estado not in _ESTADOS:
            raise ValueError(f"Estado inválido: {estado}")
        if not _HASH_RE.match(hash_entrada or ""):
            raise ValueError("hash_entrada debe ser SHA-256 en hex (64 chars).")
        if confianza is not None and not (0 <= float(confianza) <= 1):
            raise ValueError("confianza debe estar entre 0 y 1.")
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.table}
                    (tipo, entidad, id_entidad, id_usuario_actor, hash_entrada,
                     modelo, confianza, decision_final_administrador, aceptada,
                     latencia_ms, estado, codigo_error, creado_en)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING *
                """,
                (
                    tipo.strip()[:40], entidad.strip()[:60], id_entidad,
                    int(id_usuario_actor), hash_entrada.lower(),
                    modelo, float(confianza) if confianza is not None else None,
                    decision_final_administrador, aceptada,
                    max(0, int(latencia_ms)), estado, codigo_error,
                    datetime.now(timezone.utc),
                ),
            )
            return cur.fetchone()

    @classmethod
    def update_fields(cls, id_decision: int, values: dict[str, Any]) -> dict[str, Any] | None:
        allowed = cls.columns - {"id_decision", "id_usuario_actor", "hash_entrada", "creado_en"}
        payload = {k: v for k, v in values.items() if k in allowed}
        if not payload:
            return cls.get_by_id(id_decision)
        if "estado" in payload and payload["estado"] not in _ESTADOS:
            raise ValueError(f"Estado inválido: {payload['estado']}")
        names = list(payload)
        assignments = ",".join(f"{name}=%s" for name in names)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} SET {assignments} "
                f"WHERE id_decision=%s RETURNING *",
                tuple(payload[name] for name in names) + (int(id_decision),),
            )
            return cur.fetchone()


class DecisionesIAAtributosRepository(PostgresRepository):
    table = "public.decisiones_ia_atributos"
    columns = frozenset({
        "id_decision", "origen", "ruta", "tipo_valor",
        "valor_texto", "valor_numero", "valor_booleano",
    })

    @classmethod
    def list_for(cls, id_decision: int, origen: str | None = None) -> list[dict[str, Any]]:
        if origen and origen not in _ORIGENES:
            raise ValueError(f"Origen inválido: {origen}")
        where = "AND origen=%s" if origen else ""
        params: tuple = (int(id_decision), origen) if origen else (int(id_decision),)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_decision=%s {where} ORDER BY origen, ruta",
                params,
            )
            return list(cur.fetchall())

    @classmethod
    def replace_for(
        cls, id_decision: int, origen: str, atributos: list[dict[str, Any]]
    ) -> None:
        if origen not in _ORIGENES:
            raise ValueError(f"Origen inválido: {origen}")
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_decision=%s AND origen=%s",
                (int(id_decision), origen),
            )
            for attr in atributos:
                ruta = str(attr.get("ruta") or "").strip()
                tipo = str(attr.get("tipo_valor") or "").strip().lower()
                if not ruta or tipo not in _TIPOS_VALOR:
                    continue
                cur.execute(
                    f"INSERT INTO {cls.table} "
                    "(id_decision, origen, ruta, tipo_valor, "
                    " valor_texto, valor_numero, valor_booleano) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (
                        int(id_decision), origen, ruta, tipo,
                        attr.get("valor_texto") if tipo == "texto" else None,
                        attr.get("valor_numero") if tipo == "numero" else None,
                        attr.get("valor_booleano") if tipo == "booleano" else None,
                    ),
                )