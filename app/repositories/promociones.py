# app/repositories/promociones.py
"""
Repositorio de public.promociones.
Columnas del .sql:
  id_promocion, id_restaurante, descripcion, valida_hasta,
  porcentaje_descuento
"""
from __future__ import annotations

from datetime import date
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class PromocionesRepository(PostgresRepository):
    table = "public.promociones"
    columns = frozenset({
        "id_promocion", "id_restaurante", "descripcion",
        "valida_hasta", "porcentaje_descuento",
    })

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_promocion=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def list_by_restaurante(
        cls, id_restaurante: int, *, vigentes: bool = False
    ) -> list[dict[str, Any]]:
        where = ""
        params: list[Any] = [int(id_restaurante)]
        if vigentes:
            where = "AND (valida_hasta IS NULL OR valida_hasta >= CURRENT_DATE)"
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_restaurante=%s {where} "
                f"ORDER BY id_promocion",
                tuple(params),
            )
            return list(cur.fetchall())

    @classmethod
    def insert(
        cls,
        *,
        id_restaurante: int,
        descripcion: str,
        valida_hasta: date | None = None,
        porcentaje_descuento: float | None = None,
    ) -> dict[str, Any]:
        if porcentaje_descuento is not None:
            porcentaje_descuento = float(porcentaje_descuento)
            if not 0 <= porcentaje_descuento <= 100:
                raise ValueError("Porcentaje debe estar entre 0 y 100.")
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(id_restaurante, descripcion, valida_hasta, porcentaje_descuento) "
                "VALUES (%s,%s,%s,%s) RETURNING *",
                (
                    int(id_restaurante), descripcion.strip(),
                    valida_hasta, porcentaje_descuento,
                ),
            )
            return cur.fetchone()

    @classmethod
    def update_fields(cls, id_promocion: int, values: dict[str, Any]) -> dict[str, Any] | None:
        allowed = cls.columns - {"id_promocion", "id_restaurante"}
        payload = {k: v for k, v in values.items() if k in allowed}
        if not payload:
            return cls.get_by_id(id_promocion)
        if "porcentaje_descuento" in payload and payload["porcentaje_descuento"] is not None:
            v = float(payload["porcentaje_descuento"])
            if not 0 <= v <= 100:
                raise ValueError("Porcentaje debe estar entre 0 y 100.")
            payload["porcentaje_descuento"] = v
        names = list(payload)
        assignments = ",".join(f"{name}=%s" for name in names)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} SET {assignments} "
                f"WHERE id_promocion=%s RETURNING *",
                tuple(payload[name] for name in names) + (int(id_promocion),),
            )
            return cur.fetchone()