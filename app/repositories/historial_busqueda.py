# app/repositories/historial_busqueda.py
"""
Repositorio de public.historial_busqueda_recomendacion y sus 2 hijas.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class HistorialBusquedaRepository(PostgresRepository):
    table = "public.historial_busqueda_recomendacion"
    columns = frozenset({"id_historial", "id_usuario"})

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_historial=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def get_by_usuario(cls, id_usuario: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_usuario=%s "
                f"ORDER BY id_historial LIMIT 1",
                (int(id_usuario),),
            )
            return cur.fetchone()

    @classmethod
    def create_for_usuario(cls, id_usuario: int) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} (id_usuario) VALUES (%s) RETURNING *",
                (int(id_usuario),),
            )
            return cur.fetchone()


class BusquedasRecomendacionRepository(PostgresRepository):
    table = "public.busquedas_recomendacion"
    columns = frozenset({
        "id_historial", "posicion", "termino", "consulta",
        "cantidad", "ultima_busqueda",
    })

    @classmethod
    def list_for(cls, id_historial: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_historial=%s "
                f"ORDER BY posicion",
                (int(id_historial),),
            )
            return list(cur.fetchall())

    @classmethod
    def register_search(
        cls, *, id_historial: int, termino: str, consulta: str | None = None
    ) -> dict[str, Any]:
        """Registra o incrementa una búsqueda por término."""
        now = datetime.now(timezone.utc)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT posicion, cantidad FROM {cls.table} "
                f"WHERE id_historial=%s AND termino=%s",
                (int(id_historial), termino.strip()[:240]),
            )
            existente = cur.fetchone()
            if existente:
                cur.execute(
                    f"UPDATE {cls.table} "
                    f"SET cantidad=cantidad+1, ultima_busqueda=%s, "
                    f"    consulta=COALESCE(%s, consulta) "
                    f"WHERE id_historial=%s AND posicion=%s "
                    f"RETURNING *",
                    (
                        now, consulta,
                        int(id_historial), int(existente["posicion"]),
                    ),
                )
                return cur.fetchone()
            cur.execute(
                f"SELECT COALESCE(MAX(posicion),0)+1 AS next_pos "
                f"FROM {cls.table} WHERE id_historial=%s",
                (int(id_historial),),
            )
            next_pos = cur.fetchone()["next_pos"]
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(id_historial, posicion, termino, consulta, cantidad, ultima_busqueda) "
                "VALUES (%s,%s,%s,%s,1,%s) RETURNING *",
                (
                    int(id_historial), int(next_pos),
                    termino.strip()[:240], consulta, now,
                ),
            )
            return cur.fetchone()


class EnviosRecomendacionRepository(PostgresRepository):
    table = "public.envios_recomendacion"
    columns = frozenset({"id_historial", "posicion", "identificador_envio"})

    @classmethod
    def list_for(cls, id_historial: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_historial=%s "
                f"ORDER BY posicion",
                (int(id_historial),),
            )
            return list(cur.fetchall())

    @classmethod
    def append(
        cls, id_historial: int, identificador_envio: str
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT COALESCE(MAX(posicion),0)+1 AS next_pos "
                f"FROM {cls.table} WHERE id_historial=%s",
                (int(id_historial),),
            )
            next_pos = cur.fetchone()["next_pos"]
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(id_historial, posicion, identificador_envio) "
                "VALUES (%s,%s,%s) RETURNING *",
                (
                    int(id_historial), int(next_pos),
                    identificador_envio.strip(),
                ),
            )
            return cur.fetchone()