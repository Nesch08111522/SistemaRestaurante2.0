# app/repositories/sucursales.py
"""
Repositorio de public.sucursales.
Columnas del .sql:
  id_sucursal, id_empresa, nombre, direccion, distrito,
  latitud, longitud, estado, creado_en, actualizado_en
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class SucursalesRepository(PostgresRepository):
    table = "public.sucursales"
    columns = frozenset({
        "id_sucursal", "id_empresa", "nombre", "direccion",
        "distrito", "latitud", "longitud", "estado",
        "creado_en", "actualizado_en",
    })

    ESTADOS = ("draft", "active", "inactive")

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_sucursal=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def list_by_empresa(cls, id_empresa: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_empresa=%s "
                f"ORDER BY id_sucursal",
                (int(id_empresa),),
            )
            return list(cur.fetchall())

    @classmethod
    def insert(
        cls,
        *,
        id_empresa: int,
        nombre: str,
        direccion: str | None = None,
        distrito: str | None = None,
        latitud: float | None = None,
        longitud: float | None = None,
        estado: str = "active",
    ) -> dict[str, Any]:
        if estado not in cls.ESTADOS:
            raise ValueError(f"Estado inválido: {estado}")
        now = datetime.now(timezone.utc)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(id_empresa, nombre, direccion, distrito, latitud, longitud, "
                " estado, creado_en, actualizado_en) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *",
                (
                    int(id_empresa), nombre.strip(), direccion, distrito,
                    latitud, longitud, estado, now, now,
                ),
            )
            return cur.fetchone()

    @classmethod
    def update_fields(cls, id_sucursal: int, values: dict[str, Any]) -> dict[str, Any] | None:
        allowed = cls.columns - {"id_sucursal", "id_empresa", "creado_en"}
        payload = {k: v for k, v in values.items() if k in allowed}
        if not payload:
            return cls.get_by_id(id_sucursal)
        if "estado" in payload and payload["estado"] not in cls.ESTADOS:
            raise ValueError(f"Estado inválido: {payload['estado']}")
        payload["actualizado_en"] = datetime.now(timezone.utc)
        names = list(payload)
        assignments = ",".join(f"{name}=%s" for name in names)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} SET {assignments} "
                f"WHERE id_sucursal=%s RETURNING *",
                tuple(payload[name] for name in names) + (int(id_sucursal),),
            )
            return cur.fetchone()