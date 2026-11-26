"""PostgreSQL repository for tamper-evident review and AI-decision anchors."""
from __future__ import annotations

from typing import Any
from contextlib import contextmanager

from app.db.connection import connection

from app.db.repository import shared_transaction


class AnclasTrazabilidadRepository:
    table = "public.anclas_trazabilidad"

    @classmethod
    @contextmanager
    def worker_lock(cls):
        # Dedicated session lock remains held across commits and RPC calls.
        with connection(autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT pg_try_advisory_lock(%s) AS acquired", (728543201,))
                if not cur.fetchone()["acquired"]:
                    raise RuntimeError("Ya hay un worker de anclaje en ejecución.")
                try:
                    yield
                finally:
                    cur.execute("SELECT pg_advisory_unlock(%s)", (728543201,))

    @classmethod
    def enqueue(
        cls, *, tipo_recurso: str, id_recurso: int, hash_canonico: str,
        hash_previo: str | None = None,
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""INSERT INTO {cls.table}
                    (tipo_recurso, id_recurso, hash_canonico, hash_previo)
                    VALUES (%s,%s,%s,%s)
                    ON CONFLICT (tipo_recurso, id_recurso, hash_canonico)
                    DO UPDATE SET actualizado_en=CURRENT_TIMESTAMP
                    RETURNING *""",
                (tipo_recurso, int(id_recurso), hash_canonico, hash_previo),
            )
            return cur.fetchone()

    @classmethod
    def latest(cls, *, tipo_recurso: str, id_recurso: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""SELECT * FROM {cls.table} WHERE tipo_recurso=%s AND id_recurso=%s
                    ORDER BY id_ancla DESC LIMIT 1""",
                (tipo_recurso, int(id_recurso)),
            )
            return cur.fetchone()

    @classmethod
    def pending(cls, *, limit: int = 50, tipo_recurso: str | None = None) -> list[dict[str, Any]]:
        if tipo_recurso not in (None, 'resena', 'decision_ia'):
            raise ValueError('Tipo de recurso inválido.')
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""SELECT * FROM {cls.table}
                    WHERE estado IN ('pendiente', 'fallido', 'enviado', 'timeout')
                      AND (%s::text IS NULL OR tipo_recurso = %s)
                      AND (estado IN ('enviado', 'timeout') OR proximo_intento_en IS NULL OR proximo_intento_en <= CURRENT_TIMESTAMP)
                    ORDER BY (hash_transaccion IS NULL), creado_en, id_ancla FOR UPDATE SKIP LOCKED LIMIT %s""",
                (tipo_recurso, tipo_recurso, max(1, min(int(limit), 500))),
            )
            return list(cur.fetchall())

    @classmethod
    def mark(
        cls, id_ancla: int, *, estado: str, hash_transaccion: str | None = None,
        nonce_transaccion: int | None = None, enviada_en=None, proximo_intento_en=None,
        ultimo_error: str | None = None, transaccion_firmada: str | None = None,
    ) -> dict[str, Any] | None:
        if estado not in {"pendiente", "simulado", "enviado", "confirmado", "timeout", "fallido", "revertido"}:
            raise ValueError("Estado de ancla inválido.")
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""UPDATE {cls.table}
                    SET estado=%s, hash_transaccion=COALESCE(%s, hash_transaccion),
                        nonce_transaccion=COALESCE(%s, nonce_transaccion),
                        transaccion_firmada=COALESCE(%s, transaccion_firmada),
                        enviada_en=COALESCE(%s, enviada_en), proximo_intento_en=%s,
                        ultimo_error=%s, intentos=intentos+1,
                        actualizado_en=CURRENT_TIMESTAMP
                    WHERE id_ancla=%s RETURNING *""",
                (estado, hash_transaccion, nonce_transaccion, transaccion_firmada, enviada_en, proximo_intento_en,
                 ultimo_error[:500] if ultimo_error else None, int(id_ancla)),
            )
            return cur.fetchone()
