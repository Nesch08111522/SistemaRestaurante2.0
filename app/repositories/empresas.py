# app/repositories/empresas.py
"""
Repositorio de public.empresas.
Columnas del .sql:
  id_empresa, identificador_url, nombre, estado, es_demo,
  origen_alta, creado_en, actualizado_en
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class EmpresasRepository(PostgresRepository):
    table = "public.empresas"
    columns = frozenset({
        "id_empresa", "identificador_url", "nombre", "estado",
        "es_demo", "origen_alta", "creado_en", "actualizado_en",
    })

    # Estados válidos según el CHECK del .sql
    ESTADOS = frozenset({"draft", "pending_review", "active", "suspended", "archived"})

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_empresa=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def get_by_identificador(cls, identificador_url: str) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE identificador_url=%s",
                (identificador_url.strip().lower(),),
            )
            return cur.fetchone()

    @classmethod
    def list_all(cls, *, limit: int = 500) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} ORDER BY id_empresa LIMIT %s",
                (int(limit),),
            )
            return list(cur.fetchall())

    @classmethod
    def list_by_estado(cls, estado: str, *, limit: int = 500) -> list[dict[str, Any]]:
        if estado not in cls.ESTADOS:
            raise ValueError(f"Estado inválido: {estado}")
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE estado=%s ORDER BY id_empresa LIMIT %s",
                (estado, int(limit)),
            )
            return list(cur.fetchall())

    @classmethod
    def insert(
        cls,
        *,
        identificador_url: str,
        nombre: str,
        estado: str = "draft",
        es_demo: bool = False,
        origen_alta: str | None = None,
    ) -> dict[str, Any]:
        if estado not in cls.ESTADOS:
            raise ValueError(f"Estado inválido: {estado}")
        now = datetime.now(timezone.utc)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(identificador_url, nombre, estado, es_demo, origen_alta, creado_en, actualizado_en) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING *",
                (
                    identificador_url.strip().lower(),
                    nombre.strip(),
                    estado,
                    bool(es_demo),
                    origen_alta,
                    now,
                    now,
                ),
            )
            return cur.fetchone()

    @classmethod
    def update_fields(cls, id_empresa: int, values: dict[str, Any]) -> dict[str, Any] | None:
        allowed = cls.columns - {"id_empresa", "creado_en"}
        payload = {k: v for k, v in values.items() if k in allowed}
        if not payload:
            return cls.get_by_id(id_empresa)
        if "estado" in payload and payload["estado"] not in cls.ESTADOS:
            raise ValueError(f"Estado inválido: {payload['estado']}")
        payload["actualizado_en"] = datetime.now(timezone.utc)
        names = list(payload)
        assignments = ",".join(f"{name}=%s" for name in names)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} SET {assignments} "
                f"WHERE id_empresa=%s RETURNING *",
                tuple(payload[name] for name in names) + (int(id_empresa),),
            )
            return cur.fetchone()