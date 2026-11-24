# app/repositories/favoritos.py
"""
Repositorio de public.favoritos.
Columnas del .sql:
  id_favorito, id_usuario, id_restaurante, marcado_en
Constraint UNIQUE (id_usuario, id_restaurante).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class FavoritosRepository(PostgresRepository):
    table = "public.favoritos"
    columns = frozenset({"id_favorito", "id_usuario", "id_restaurante", "marcado_en"})

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_favorito=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def list_by_usuario(cls, id_usuario: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_usuario=%s "
                f"ORDER BY marcado_en DESC, id_favorito DESC",
                (int(id_usuario),),
            )
            return list(cur.fetchall())

    @classmethod
    def exists(cls, id_usuario: int, id_restaurante: int) -> bool:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT 1 FROM {cls.table} "
                f"WHERE id_usuario=%s AND id_restaurante=%s",
                (int(id_usuario), int(id_restaurante)),
            )
            return cur.fetchone() is not None

    @classmethod
    def add(cls, id_usuario: int, id_restaurante: int) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(id_usuario, id_restaurante, marcado_en) "
                "VALUES (%s,%s,%s) "
                "ON CONFLICT (id_usuario, id_restaurante) "
                "DO UPDATE SET marcado_en=EXCLUDED.marcado_en "
                "RETURNING *",
                (int(id_usuario), int(id_restaurante), now),
            )
            return cur.fetchone()

    @classmethod
    def remove(cls, id_usuario: int, id_restaurante: int) -> bool:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} "
                f"WHERE id_usuario=%s AND id_restaurante=%s",
                (int(id_usuario), int(id_restaurante)),
            )
            return cur.rowcount >= 1