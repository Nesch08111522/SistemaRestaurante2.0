# app/repositories/seguridad.py
"""
Repositorio de seguridad:
  - public.seguridad_cuentas
  - public.limites_autenticacion
  - public.desafios_contrasena
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class SeguridadCuentasRepository(PostgresRepository):
    table = "public.seguridad_cuentas"
    columns = frozenset({"id_cuenta", "hash_recuperacion"})

    @classmethod
    def get_for(cls, id_cuenta: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_cuenta=%s",
                (int(id_cuenta),),
            )
            return cur.fetchone()

    @classmethod
    def upsert_for(cls, id_cuenta: int, hash_recuperacion: str) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.table} (id_cuenta, hash_recuperacion)
                VALUES (%s,%s)
                ON CONFLICT (id_cuenta) DO UPDATE
                SET hash_recuperacion=EXCLUDED.hash_recuperacion
                RETURNING *
                """,
                (int(id_cuenta), hash_recuperacion),
            )
            return cur.fetchone()


class LimitesAutenticacionRepository(PostgresRepository):
    table = "public.limites_autenticacion"
    columns = frozenset({
        "id_limite", "cantidad", "iniciado_epoch",
        "creado_en", "actualizado_en",
    })

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_limite=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def increment(
        cls, id_limite: int, *, maximo: int | None = None
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT cantidad FROM {cls.table} WHERE id_limite=%s FOR UPDATE",
                (int(id_limite),),
            )
            row = cur.fetchone()
            if not row:
                raise LookupError("Límite no encontrado.")
            nueva = int(row["cantidad"]) + 1
            if maximo is not None and nueva > maximo:
                raise ValueError(f"Límite excedido: máximo {maximo}.")
            now = datetime.now(timezone.utc)
            cur.execute(
                f"UPDATE {cls.table} SET cantidad=%s, actualizado_en=%s "
                f"WHERE id_limite=%s RETURNING *",
                (nueva, now, int(id_limite)),
            )
            return cur.fetchone()

    @classmethod
    def reset(cls, id_limite: int) -> dict[str, Any] | None:
        now = datetime.now(timezone.utc)
        epoch = int(now.timestamp())
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} "
                f"SET cantidad=0, iniciado_epoch=%s, actualizado_en=%s "
                f"WHERE id_limite=%s RETURNING *",
                (epoch, now, int(id_limite)),
            )
            return cur.fetchone()


class DesafiosContrasenaRepository(PostgresRepository):
    table = "public.desafios_contrasena"
    columns = frozenset({
        "id_desafio", "hash_codigo", "codigo_desafio", "canal",
        "epoch", "intentos", "utilizado", "entregado",
        "emitido_en", "vence_en", "hash_contacto",
    })

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_desafio=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def latest_for_contacto(cls, hash_contacto: str) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE hash_contacto=%s "
                f"ORDER BY id_desafio DESC LIMIT 1",
                (hash_contacto,),
            )
            return cur.fetchone()

    @classmethod
    def create(
        cls,
        *,
        hash_codigo: str,
        canal: str,
        hash_contacto: str,
        codigo_desafio: str | None = None,
        vence_en: datetime | None = None,
        epoch: int = 0,
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(hash_codigo, codigo_desafio, canal, epoch, intentos, "
                " utilizado, entregado, emitido_en, vence_en, hash_contacto) "
                "VALUES (%s,%s,%s,%s,0,FALSE,FALSE,%s,%s,%s) RETURNING *",
                (
                    hash_codigo, codigo_desafio, canal.strip()[:30],
                    int(epoch), datetime.now(timezone.utc), vence_en,
                    hash_contacto,
                ),
            )
            return cur.fetchone()

    @classmethod
    def increment_attempts(cls, id_desafio: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} SET intentos=intentos+1 "
                f"WHERE id_desafio=%s RETURNING *",
                (int(id_desafio),),
            )
            return cur.fetchone()

    @classmethod
    def mark_used(cls, id_desafio: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} SET utilizado=TRUE "
                f"WHERE id_desafio=%s RETURNING *",
                (int(id_desafio),),
            )
            return cur.fetchone()

    @classmethod
    def mark_delivered(cls, id_desafio: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} SET entregado=TRUE "
                f"WHERE id_desafio=%s RETURNING *",
                (int(id_desafio),),
            )
            return cur.fetchone()