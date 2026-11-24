# app/repositories/notificaciones.py
"""
Repositorio de public.notificaciones.
Columnas del .sql:
  id_notificacion, id_usuario, tipo, titulo, mensaje,
  enlace, leida, creada_en
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class NotificacionesRepository(PostgresRepository):
    table = "public.notificaciones"
    columns = frozenset({
        "id_notificacion", "id_usuario", "tipo", "titulo", "mensaje",
        "enlace", "leida", "creada_en",
    })

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_notificacion=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def list_by_usuario(
        cls, id_usuario: int, *, only_unread: bool = False, limit: int = 50
    ) -> list[dict[str, Any]]:
        where = "AND leida=FALSE" if only_unread else ""
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_usuario=%s {where} "
                f"ORDER BY creada_en DESC LIMIT %s",
                (int(id_usuario), int(limit)),
            )
            return list(cur.fetchall())

    @classmethod
    def insert(
        cls,
        *,
        id_usuario: int,
        tipo: str,
        titulo: str,
        mensaje: str,
        enlace: str | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(id_usuario, tipo, titulo, mensaje, enlace, leida, creada_en) "
                "VALUES (%s,%s,%s,%s,%s,FALSE,%s) RETURNING *",
                (
                    int(id_usuario), tipo.strip()[:40],
                    titulo.strip()[:180], mensaje.strip(),
                    enlace, now,
                ),
            )
            return cur.fetchone()

    @classmethod
    def insert_many(
        cls,
        *,
        ids_usuarios: list[int],
        tipo: str,
        titulo: str,
        mensaje: str,
        enlace: str | None = None,
    ) -> list[dict[str, Any]]:
        resultados: list[dict[str, Any]] = []
        now = datetime.now(timezone.utc)
        with shared_transaction() as conn, conn.cursor() as cur:
            for uid in ids_usuarios:
                cur.execute(
                    f"INSERT INTO {cls.table} "
                    "(id_usuario, tipo, titulo, mensaje, enlace, leida, creada_en) "
                    "VALUES (%s,%s,%s,%s,%s,FALSE,%s) RETURNING *",
                    (
                        int(uid), tipo.strip()[:40],
                        titulo.strip()[:180], mensaje.strip(),
                        enlace, now,
                    ),
                )
                row = cur.fetchone()
                if row:
                    resultados.append(row)
        return resultados

    @classmethod
    def mark_read(cls, id_notificacion: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} SET leida=TRUE "
                f"WHERE id_notificacion=%s RETURNING *",
                (int(id_notificacion),),
            )
            return cur.fetchone()

    @classmethod
    def mark_all_read(cls, id_usuario: int) -> int:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} SET leida=TRUE "
                f"WHERE id_usuario=%s AND leida=FALSE",
                (int(id_usuario),),
            )
            return cur.rowcount

    @classmethod
    def count_unread(cls, id_usuario: int) -> int:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT COUNT(*) AS total FROM {cls.table} "
                f"WHERE id_usuario=%s AND leida=FALSE",
                (int(id_usuario),),
            )
            row = cur.fetchone()
            return int(row["total"]) if row else 0