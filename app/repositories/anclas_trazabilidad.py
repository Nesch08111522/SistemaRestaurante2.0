"""PostgreSQL repository for tamper-evident review and AI-decision anchors."""
from __future__ import annotations

from typing import Any

from app.db.repository import shared_transaction


class AnclasTrazabilidadRepository:
    table = "public.anclas_trazabilidad"

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
    def pending(cls, *, limit: int = 50) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""SELECT * FROM {cls.table}
                    WHERE estado IN ('pendiente', 'fallido', 'enviado', 'timeout')
                      AND (proximo_intento_en IS NULL OR proximo_intento_en <= CURRENT_TIMESTAMP)
                    ORDER BY creado_en, id_ancla FOR UPDATE SKIP LOCKED LIMIT %s""",
                (max(1, min(int(limit), 500)),),
            )
            return list(cur.fetchall())

    @classmethod
    def mark(
        cls, id_ancla: int, *, estado: str, hash_transaccion: str | None = None,
        nonce_transaccion: int | None = None, enviada_en=None, proximo_intento_en=None,
        ultimo_error: str | None = None,
    ) -> dict[str, Any] | None:
        if estado not in {"pendiente", "simulado", "enviado", "confirmado", "timeout", "fallido", "revertido"}:
            raise ValueError("Estado de ancla inválido.")
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""UPDATE {cls.table}
                    SET estado=%s, hash_transaccion=COALESCE(%s, hash_transaccion),
                        nonce_transaccion=COALESCE(%s, nonce_transaccion),
                        enviada_en=COALESCE(%s, enviada_en), proximo_intento_en=%s,
                        ultimo_error=%s, intentos=intentos+1,
                        actualizado_en=CURRENT_TIMESTAMP
                    WHERE id_ancla=%s RETURNING *""",
                (estado, hash_transaccion, nonce_transaccion, enviada_en, proximo_intento_en,
                 (ultimo_error or None)[:500], int(id_ancla)),
            )
            return cur.fetchone()
