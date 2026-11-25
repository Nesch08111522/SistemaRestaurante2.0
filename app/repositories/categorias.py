# app/repositories/categorias.py
"""
Repositorio de public.categorias.
Columnas del .sql:
  id_categoria, nombre, slug, icono, url_imagen
"""
from __future__ import annotations

from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class CategoriasRepository(PostgresRepository):
    table = "public.categorias"
    columns = frozenset({"id_categoria", "nombre", "slug", "icono", "url_imagen"})

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_categoria=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def get_by_slug(cls, slug: str) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE slug=%s",
                (slug.strip().lower(),),
            )
            return cur.fetchone()

    @classmethod
    def list_all(cls) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {cls.table} ORDER BY nombre")
            return list(cur.fetchall())

    @classmethod
    def insert(
        cls,
        *,
        nombre: str,
        slug: str,
        icono: str | None = None,
        url_imagen: str | None = None,
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} (nombre, slug, icono, url_imagen) "
                f"VALUES (%s,%s,%s,%s) RETURNING *",
                (nombre.strip(), slug.strip().lower(), icono, url_imagen),
            )
            return cur.fetchone()