# app/repositories/categorias_plato.py
"""
Repositorio de public.categorias_plato.
Columnas del .sql: nombre (PK).
"""
from __future__ import annotations

from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class CategoriasPlatoRepository(PostgresRepository):
    table = "public.categorias_plato"
    columns = frozenset({"nombre"})

    @classmethod
    def list_all(cls) -> list[str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(f"SELECT nombre FROM {cls.table} ORDER BY nombre")
            return [row["nombre"] for row in cur.fetchall()]

    @classmethod
    def exists(cls, nombre: str) -> bool:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT 1 FROM {cls.table} WHERE nombre=%s",
                (nombre.strip(),),
            )
            return cur.fetchone() is not None

    @classmethod
    def insert(cls, nombre: str) -> str:
        clean = " ".join(nombre.strip().split())[:80]
        if not clean:
            raise ValueError("El nombre de categoría no puede estar vacío.")
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} (nombre) VALUES (%s) "
                f"ON CONFLICT (nombre) DO NOTHING RETURNING nombre",
                (clean,),
            )
            row = cur.fetchone()
            return row["nombre"] if row else clean