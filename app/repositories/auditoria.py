# app/repositories/auditoria.py
"""
Repositorio de public.eventos_auditoria y eventos_auditoria_atributos.
Columnas de eventos_auditoria:
  id_evento, id_usuario_actor, id_empresa, accion, tipo_recurso,
  id_recurso, id_solicitud (UUID), hash_ip (SHA-256), creado_en
Columnas de eventos_auditoria_atributos:
  id_evento, ruta, tipo_valor, valor_texto, valor_numero, valor_booleano
"""
from __future__ import annotations

import uuid as _uuid
from datetime import datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


_TIPOS_VALOR = frozenset({"texto", "numero", "booleano", "nulo"})


class EventosAuditoriaRepository(PostgresRepository):
    table = "public.eventos_auditoria"
    columns = frozenset({
        "id_evento", "id_usuario_actor", "id_empresa", "accion",
        "tipo_recurso", "id_recurso", "id_solicitud", "hash_ip", "creado_en",
    })

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_evento=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def list_by_actor(
        cls, id_usuario_actor: int, *, limit: int = 100
    ) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_usuario_actor=%s "
                f"ORDER BY creado_en DESC LIMIT %s",
                (int(id_usuario_actor), int(limit)),
            )
            return list(cur.fetchall())

    @classmethod
    def list_by_empresa(
        cls, id_empresa: int, *, limit: int = 100
    ) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_empresa=%s "
                f"ORDER BY creado_en DESC LIMIT %s",
                (int(id_empresa), int(limit)),
            )
            return list(cur.fetchall())

    @classmethod
    def record(
        cls,
        *,
        accion: str,
        tipo_recurso: str,
        id_usuario_actor: int | None = None,
        id_empresa: int | None = None,
        id_recurso: str | None = None,
        id_solicitud: str | None = None,
        hash_ip: str | None = None,
        atributos: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if id_solicitud:
            try:
                _uuid.UUID(id_solicitud)
            except ValueError:
                raise ValueError("id_solicitud debe ser UUID válido.") from None
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(id_usuario_actor, id_empresa, accion, tipo_recurso, id_recurso, "
                " id_solicitud, hash_ip, creado_en) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *",
                (
                    id_usuario_actor, id_empresa, accion.strip()[:140],
                    tipo_recurso.strip()[:100], id_recurso, id_solicitud,
                    hash_ip, datetime.now(timezone.utc),
                ),
            )
            row = cur.fetchone()
            event_id = row["id_evento"]
            if atributos:
                for attr in atributos:
                    ruta = str(attr.get("ruta") or "").strip()
                    tipo = str(attr.get("tipo_valor") or "").strip().lower()
                    if not ruta or tipo not in _TIPOS_VALOR:
                        continue
                    cur.execute(
                        "INSERT INTO public.eventos_auditoria_atributos "
                        "(id_evento, ruta, tipo_valor, valor_texto, "
                        " valor_numero, valor_booleano) "
                        "VALUES (%s,%s,%s,%s,%s,%s)",
                        (
                            int(event_id), ruta, tipo,
                            attr.get("valor_texto") if tipo == "texto" else None,
                            attr.get("valor_numero") if tipo == "numero" else None,
                            attr.get("valor_booleano") if tipo == "booleano" else None,
                        ),
                    )
            return row


class EventosAuditoriaAtributosRepository(PostgresRepository):
    table = "public.eventos_auditoria_atributos"
    columns = frozenset({
        "id_evento", "ruta", "tipo_valor",
        "valor_texto", "valor_numero", "valor_booleano",
    })

    @classmethod
    def list_for(cls, id_evento: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_evento=%s ORDER BY ruta",
                (int(id_evento),),
            )
            return list(cur.fetchall())