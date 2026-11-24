# app/repositories/resenas.py
"""
Repositorio de public.resenas.
Columnas del .sql:
  id_resena, id_restaurante, id_usuario, calificacion,
  comentario, creado_en, actualizado_en
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class ResenasRepository(PostgresRepository):
    table = "public.resenas"
    columns = frozenset({
        "id_resena", "id_restaurante", "id_usuario", "calificacion",
        "comentario", "creado_en", "actualizado_en",
    })

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_resena=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def list_by_restaurante(
        cls, id_restaurante: int, *, limit: int = 100
    ) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_restaurante=%s "
                f"ORDER BY creado_en DESC NULLS LAST, id_resena DESC LIMIT %s",
                (int(id_restaurante), int(limit)),
            )
            return list(cur.fetchall())

    @classmethod
    def list_by_usuario(
        cls, id_usuario: int, *, limit: int = 100
    ) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_usuario=%s "
                f"ORDER BY creado_en DESC NULLS LAST LIMIT %s",
                (int(id_usuario), int(limit)),
            )
            return list(cur.fetchall())

    @classmethod
    def exists_for(
        cls, id_usuario: int, id_restaurante: int
    ) -> bool:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT 1 FROM {cls.table} "
                f"WHERE id_usuario=%s AND id_restaurante=%s LIMIT 1",
                (int(id_usuario), int(id_restaurante)),
            )
            return cur.fetchone() is not None

    @classmethod
    def insert(
        cls,
        *,
        id_restaurante: int,
        id_usuario: int,
        calificacion: int,
        comentario: str | None = None,
    ) -> dict[str, Any]:
        if not 1 <= int(calificacion) <= 5:
            raise ValueError("Calificación debe estar entre 1 y 5.")
        now = datetime.now(timezone.utc)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(id_restaurante, id_usuario, calificacion, comentario, "
                " creado_en, actualizado_en) "
                "VALUES (%s,%s,%s,%s,%s,%s) RETURNING *",
                (
                    int(id_restaurante), int(id_usuario), int(calificacion),
                    comentario, now, now,
                ),
            )
            return cur.fetchone()

    @classmethod
    def update_fields(cls, id_resena: int, values: dict[str, Any]) -> dict[str, Any] | None:
        allowed = cls.columns - {"id_resena", "id_restaurante", "id_usuario", "creado_en"}
        payload = {k: v for k, v in values.items() if k in allowed}
        if not payload:
            return cls.get_by_id(id_resena)
        if "calificacion" in payload and not 1 <= int(payload["calificacion"]) <= 5:
            raise ValueError("Calificación debe estar entre 1 y 5.")
        payload["actualizado_en"] = datetime.now(timezone.utc)
        names = list(payload)
        assignments = ",".join(f"{name}=%s" for name in names)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} SET {assignments} "
                f"WHERE id_resena=%s RETURNING *",
                tuple(payload[name] for name in names) + (int(id_resena),),
            )
            return cur.fetchone()

    @classmethod
    def average_for_restaurante(cls, id_restaurante: int) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) AS total, "
                f"COALESCE(AVG(calificacion),0) AS promedio "
                f"FROM {cls.table} WHERE id_restaurante=%s",
                (int(id_restaurante),),
            )
            row = cur.fetchone()
            return {
                "total_resenas": int(row["total"]) if row else 0,
                "promedio_calificacion": float(row["promedio"]) if row else 0.0,
            }