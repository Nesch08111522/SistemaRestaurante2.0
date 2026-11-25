# app/repositories/mapa_migracion.py
"""
Repositorio de public.mapa_migracion_origen.
Columnas del .sql:
  coleccion_origen, id_origen, tabla_destino, id_destino,
  origen_creado_en, origen_actualizado_en
PK compuesta (coleccion_origen, id_origen).
"""
from __future__ import annotations

from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class MapaMigracionOrigenRepository(PostgresRepository):
    table = "public.mapa_migracion_origen"
    columns = frozenset({
        "coleccion_origen", "id_origen", "tabla_destino", "id_destino",
        "origen_creado_en", "origen_actualizado_en",
    })

    @classmethod
    def get(
        cls, coleccion_origen: str, id_origen: int
    ) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} "
                f"WHERE coleccion_origen=%s AND id_origen=%s",
                (coleccion_origen.strip()[:80], int(id_origen)),
            )
            return cur.fetchone()

    @classmethod
    def record(
        cls,
        *,
        coleccion_origen: str,
        id_origen: int,
        tabla_destino: str,
        id_destino: int,
        origen_creado_en=None,
        origen_actualizado_en=None,
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.table}
                    (coleccion_origen, id_origen, tabla_destino, id_destino,
                     origen_creado_en, origen_actualizado_en)
                VALUES (%s,%s,%s,%s,%s,%s)
                ON CONFLICT (coleccion_origen, id_origen) DO UPDATE
                SET tabla_destino=EXCLUDED.tabla_destino,
                    id_destino=EXCLUDED.id_destino,
                    origen_creado_en=EXCLUDED.origen_creado_en,
                    origen_actualizado_en=EXCLUDED.origen_actualizado_en
                RETURNING *
                """,
                (
                    coleccion_origen.strip()[:80], int(id_origen),
                    tabla_destino.strip()[:100], int(id_destino),
                    origen_creado_en, origen_actualizado_en,
                ),
            )
            return cur.fetchone()