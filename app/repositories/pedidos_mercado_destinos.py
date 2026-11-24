# app/repositories/pedidos_mercado_destinos.py
"""
Repositorio de public.pedidos_mercado_destinos.
Columnas del .sql:
  id_pedido, destinatario, telefono, direccion, distrito,
  ciudad, referencia, latitud, longitud
"""
from __future__ import annotations

from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class PedidosMercadoDestinosRepository(PostgresRepository):
    table = "public.pedidos_mercado_destinos"
    columns = frozenset({
        "id_pedido", "destinatario", "telefono", "direccion",
        "distrito", "ciudad", "referencia", "latitud", "longitud",
    })

    @classmethod
    def get_for(cls, id_pedido: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_pedido=%s",
                (int(id_pedido),),
            )
            return cur.fetchone()

    @classmethod
    def upsert_for(
        cls,
        *,
        id_pedido: int,
        destinatario: str | None = None,
        telefono: str | None = None,
        direccion: str | None = None,
        distrito: str | None = None,
        ciudad: str | None = None,
        referencia: str | None = None,
        latitud: float | None = None,
        longitud: float | None = None,
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.table}
                    (id_pedido, destinatario, telefono, direccion,
                     distrito, ciudad, referencia, latitud, longitud)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id_pedido) DO UPDATE
                SET destinatario=EXCLUDED.destinatario,
                    telefono=EXCLUDED.telefono,
                    direccion=EXCLUDED.direccion,
                    distrito=EXCLUDED.distrito,
                    ciudad=EXCLUDED.ciudad,
                    referencia=EXCLUDED.referencia,
                    latitud=EXCLUDED.latitud,
                    longitud=EXCLUDED.longitud
                RETURNING *
                """,
                (
                    int(id_pedido), destinatario, telefono, direccion,
                    distrito, ciudad, referencia, latitud, longitud,
                ),
            )
            return cur.fetchone()