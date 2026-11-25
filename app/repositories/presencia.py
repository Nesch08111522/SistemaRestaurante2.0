# app/repositories/presencia.py
"""
Repositorio de public.presencia_sistema.
Columnas del .sql: id_presencia, presente_en, epoch
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class PresenciaRepository(PostgresRepository):
    table = "public.presencia_sistema"
    columns = frozenset({"id_presencia", "presente_en", "epoch"})

    @classmethod
    def latest(cls) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} ORDER BY presente_en DESC LIMIT 1"
            )
            return cur.fetchone()

    @classmethod
    def heartbeat(cls, epoch: str) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} (presente_en, epoch) "
                f"VALUES (%s,%s) RETURNING *",
                (datetime.now(timezone.utc), epoch.strip()[:40]),
            )
            return cur.fetchone()