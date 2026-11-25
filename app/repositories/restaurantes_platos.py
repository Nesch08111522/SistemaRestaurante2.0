# app/repositories/restaurantes_platos.py
"""
Repositorio de public.restaurantes_platos.
Columnas del .sql: id_restaurante, posicion, id_plato.
"""
from __future__ import annotations

from app.db.repository import PostgresRepository, shared_transaction


class RestaurantesPlatosRepository(PostgresRepository):
    table = "public.restaurantes_platos"
    columns = frozenset({"id_restaurante", "posicion", "id_plato"})

    @classmethod
    def list_plato_ids(cls, id_restaurante: int) -> list[int]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT id_plato FROM {cls.table} "
                f"WHERE id_restaurante=%s ORDER BY posicion",
                (int(id_restaurante),),
            )
            return [row["id_plato"] for row in cur.fetchall()]

    @classmethod
    def replace_for(cls, id_restaurante: int, plato_ids: list[int]) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_restaurante=%s",
                (int(id_restaurante),),
            )
            pos = 0
            vistos = set()
            for pid in plato_ids:
                pid = int(pid)
                if pid in vistos:
                    continue
                vistos.add(pid)
                pos += 1
                cur.execute(
                    f"INSERT INTO {cls.table} (id_restaurante, posicion, id_plato) "
                    f"VALUES (%s,%s,%s)",
                    (int(id_restaurante), pos, pid),
                )