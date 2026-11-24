# app/repositories/consultas_comerciales.py
"""
Repositorio de public.consultas_comerciales.
Columnas del .sql:
  id_consulta, id_usuario_actor, estado, radio_km,
  latitud, longitud, consultada_en
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class ConsultasComercialesRepository(PostgresRepository):
    table = "public.consultas_comerciales"
    columns = frozenset({
        "id_consulta", "id_usuario_actor", "estado", "radio_km",
        "latitud", "longitud", "consultada_en",
    })

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_consulta=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def list_by_actor(
        cls, id_usuario_actor: int, *, limit: int = 50
    ) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_usuario_actor=%s "
                f"ORDER BY consultada_en DESC LIMIT %s",
                (int(id_usuario_actor), int(limit)),
            )
            return list(cur.fetchall())

    @classmethod
    def register(
        cls,
        *,
        id_usuario_actor: int | None,
        estado: str,
        radio_km: float | None = None,
        latitud: float | None = None,
        longitud: float | None = None,
    ) -> dict[str, Any]:
        if latitud is not None and not -90 <= latitud <= 90:
            raise ValueError("Latitud fuera de rango.")
        if longitud is not None and not -180 <= longitud <= 180:
            raise ValueError("Longitud fuera de rango.")
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(id_usuario_actor, estado, radio_km, latitud, longitud, consultada_en) "
                "VALUES (%s,%s,%s,%s,%s,%s) RETURNING *",
                (
                    id_usuario_actor, estado.strip()[:40], radio_km,
                    latitud, longitud, datetime.now(timezone.utc),
                ),
            )
            return cur.fetchone()