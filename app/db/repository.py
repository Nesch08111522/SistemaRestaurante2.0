# app/db/repository.py
"""Primitivas de repositorio PostgreSQL relacionales.

Las subclases declaran `table` y `columns` en código.
Nunca se acepta table/column desde el request; los valores siempre se parametrizan.
"""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, ClassVar

from app.db.connection import connection, transaction_limits


_shared_connection = ContextVar("shared_connection", default=None)


@contextmanager
def shared_transaction():
    """
    Comparte una misma conexión/transacción a través de varias operaciones
    (por ejemplo: crear un usuario y su fila de preferencias en un solo commit).
    """
    active = _shared_connection.get()
    if active is not None:
        yield active
        return
    with connection() as conn, conn.transaction():
        transaction_limits(conn)
        token = _shared_connection.set(conn)
        try:
            yield conn
        finally:
            _shared_connection.reset(token)


class PostgresRepository:
    """Repositorio relacional mínimo. Subclases deben declarar table + columns."""

    table: ClassVar[str]
    columns: ClassVar[frozenset[str]]

    @classmethod
    def _validate_mapping(cls, values: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(values, dict):
            raise TypeError("values debe ser un objeto")
        unknown = set(values) - set(cls.columns)
        if unknown:
            raise ValueError(f"Campos no permitidos: {sorted(unknown)}")
        return values

    @classmethod
    def all(cls, *, limit: int = 1000, offset: int = 0) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 5000))
        offset = max(0, int(offset))
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} ORDER BY 1 LIMIT %s OFFSET %s",
                (limit, offset),
            )
            return list(cur.fetchall())

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def create(cls, values: dict[str, Any]) -> dict[str, Any]:
        values = cls._validate_mapping(values)
        if not values:
            raise ValueError("No hay campos para insertar")
        names = list(values)
        placeholders = ",".join(["%s"] * len(names))
        query = (
            f"INSERT INTO {cls.table} ({','.join(names)}) "
            f"VALUES ({placeholders}) RETURNING *"
        )
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(query, tuple(values[name] for name in names))
            return cur.fetchone()

    @classmethod
    def update(cls, item_id: int, values: dict[str, Any]) -> dict[str, Any] | None:
        values = cls._validate_mapping(values)
        if not values:
            raise ValueError("No hay campos para actualizar")
        names = list(values)
        assignments = ",".join(f"{name}=%s" for name in names)
        query = (
            f"UPDATE {cls.table} SET {assignments} "
            f"WHERE id=%s RETURNING *"
        )
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                query,
                tuple(values[name] for name in names) + (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def delete(cls, item_id: int) -> bool:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id=%s",
                (int(item_id),),
            )
            return cur.rowcount == 1