# app/repositories/membresias.py
"""
Repositorio de public.membresias.
Columnas del .sql:
  id_membresia, id_usuario, id_empresa, rol, estado,
  creado_en, actualizado_en

Nota: el .sql NO tiene branch_memberships. El alcance por sucursal se
gestiona con `sucursales` + `restaurantes`. Si en el futuro se requiere
alcance por sucursal, se agrega una tabla nueva.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class MembresiasRepository(PostgresRepository):
    table = "public.membresias"
    columns = frozenset({
        "id_membresia", "id_usuario", "id_empresa", "rol",
        "estado", "creado_en", "actualizado_en",
    })

    ROLES = (
        "business_owner", "business_admin", "manager",
        "cashier", "waiter", "kitchen",
    )
    ESTADOS = ("invited", "active", "revoked")

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_membresia=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def get_for_user_empresa(
        cls, id_usuario: int, id_empresa: int
    ) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} "
                f"WHERE id_usuario=%s AND id_empresa=%s",
                (int(id_usuario), int(id_empresa)),
            )
            return cur.fetchone()

    @classmethod
    def list_by_usuario(cls, id_usuario: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} "
                f"WHERE id_usuario=%s AND estado IN ('active','invited') "
                f"ORDER BY id_membresia",
                (int(id_usuario),),
            )
            return list(cur.fetchall())

    @classmethod
    def list_by_empresa(
        cls, id_empresa: int, *, only_active: bool = True
    ) -> list[dict[str, Any]]:
        where = "AND estado='active'" if only_active else ""
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} "
                f"WHERE id_empresa=%s {where} ORDER BY id_membresia",
                (int(id_empresa),),
            )
            return list(cur.fetchall())

    @classmethod
    def has_active_role(
        cls, id_usuario: int, id_empresa: int, roles: tuple[str, ...]
    ) -> bool:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT rol FROM {cls.table} "
                f"WHERE id_usuario=%s AND id_empresa=%s AND estado='active'",
                (int(id_usuario), int(id_empresa)),
            )
            row = cur.fetchone()
            return bool(row and row["rol"] in roles)

    @classmethod
    def insert(
        cls,
        *,
        id_usuario: int,
        id_empresa: int,
        rol: str,
        estado: str = "active",
    ) -> dict[str, Any]:
        if rol not in cls.ROLES:
            raise ValueError(f"Rol inválido: {rol}")
        if estado not in cls.ESTADOS:
            raise ValueError(f"Estado inválido: {estado}")
        now = datetime.now(timezone.utc)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(id_usuario, id_empresa, rol, estado, creado_en, actualizado_en) "
                "VALUES (%s,%s,%s,%s,%s,%s) RETURNING *",
                (int(id_usuario), int(id_empresa), rol, estado, now, now),
            )
            return cur.fetchone()

    @classmethod
    def set_estado(cls, id_membresia: int, estado: str) -> dict[str, Any] | None:
        if estado not in cls.ESTADOS:
            raise ValueError(f"Estado inválido: {estado}")
        now = datetime.now(timezone.utc)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} SET estado=%s, actualizado_en=%s "
                f"WHERE id_membresia=%s RETURNING *",
                (estado, now, int(id_membresia)),
            )
            return cur.fetchone()