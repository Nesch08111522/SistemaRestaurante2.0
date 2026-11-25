# app/repositories/pedidos_mercado_historial.py
"""
Repositorio de public.pedidos_mercado_historial_estados.
Columnas del .sql:
  id_pedido, posicion, estado, ocurrido_en
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class PedidosMercadoHistorialRepository(PostgresRepository):
    table = "public.pedidos_mercado_historial_estados"
    columns = frozenset({"id_pedido", "posicion", "estado", "ocurrido_en"})

    @classmethod
    def list_for(cls, id_pedido: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} "
                f"WHERE id_pedido=%s ORDER BY posicion",
                (int(id_pedido),),
            )
            return list(cur.fetchall())

    @classmethod
    def append(
        cls, id_pedido: int, estado: str
    ) -> dict[str, Any]:
        """Añade un estado al historial con la siguiente posición."""
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT COALESCE(MAX(posicion),0)+1 AS next_pos "
                f"FROM {cls.table} WHERE id_pedido=%s",
                (int(id_pedido),),
            )
            next_pos = cur.fetchone()["next_pos"]
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(id_pedido, posicion, estado, ocurrido_en) "
                "VALUES (%s,%s,%s,%s) RETURNING *",
                (
                    int(id_pedido), int(next_pos),
                    estado.strip()[:60], datetime.now(timezone.utc),
                ),
            )
            return cur.fetchone()