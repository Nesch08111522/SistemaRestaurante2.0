# app/repositories/pedidos_mercado_lineas.py
"""
Repositorios de las líneas de pedido y sus hijas.

Columnas de pedidos_mercado_lineas:
  id_pedido, posicion, id_plato, id_oferta, nombre_snapshot,
  cantidad, precio_unitario, costo, ahorro

Columnas de pedidos_mercado_lineas_adicionales:
  id_pedido, posicion_linea, posicion_adicional, adicional

Columnas de pedidos_mercado_lineas_usos:
  id_pedido, posicion_linea, ruta, tipo_valor, valor_texto,
  valor_numero, valor_booleano
"""
from __future__ import annotations

from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class PedidosMercadoLineasRepository(PostgresRepository):
    table = "public.pedidos_mercado_lineas"
    columns = frozenset({
        "id_pedido", "posicion", "id_plato", "id_oferta",
        "nombre_snapshot", "cantidad", "precio_unitario", "costo", "ahorro",
    })

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
    def insert_line(
        cls,
        *,
        id_pedido: int,
        posicion: int,
        nombre_snapshot: str,
        cantidad: int,
        precio_unitario: float,
        id_plato: int | None = None,
        id_oferta: int | None = None,
        costo: float | None = None,
        ahorro: float = 0,
    ) -> dict[str, Any]:
        if int(cantidad) <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")
        if float(precio_unitario) < 0:
            raise ValueError("El precio unitario no puede ser negativo.")
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(id_pedido, posicion, id_plato, id_oferta, nombre_snapshot, "
                " cantidad, precio_unitario, costo, ahorro) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *",
                (
                    int(id_pedido), int(posicion), id_plato, id_oferta,
                    nombre_snapshot.strip()[:180], int(cantidad),
                    float(precio_unitario), costo, float(ahorro),
                ),
            )
            return cur.fetchone()


class PedidosMercadoLineasAdicionalesRepository(PostgresRepository):
    table = "public.pedidos_mercado_lineas_adicionales"
    columns = frozenset({
        "id_pedido", "posicion_linea", "posicion_adicional", "adicional",
    })

    @classmethod
    def list_for(cls, id_pedido: int, posicion_linea: int) -> list[str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT adicional FROM {cls.table} "
                f"WHERE id_pedido=%s AND posicion_linea=%s "
                f"ORDER BY posicion_adicional",
                (int(id_pedido), int(posicion_linea)),
            )
            return [row["adicional"] for row in cur.fetchall()]

    @classmethod
    def replace_for_line(
        cls, id_pedido: int, posicion_linea: int, adicionales: list[str]
    ) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} "
                f"WHERE id_pedido=%s AND posicion_linea=%s",
                (int(id_pedido), int(posicion_linea)),
            )
            pos = 0
            for adicional in adicionales:
                clean = " ".join(str(adicional).strip().split())
                if not clean:
                    continue
                pos += 1
                cur.execute(
                    f"INSERT INTO {cls.table} "
                    "(id_pedido, posicion_linea, posicion_adicional, adicional) "
                    "VALUES (%s,%s,%s,%s)",
                    (int(id_pedido), int(posicion_linea), pos, clean),
                )


class PedidosMercadoLineasUsosRepository(PostgresRepository):
    table = "public.pedidos_mercado_lineas_usos"
    columns = frozenset({
        "id_pedido", "posicion_linea", "ruta",
        "tipo_valor", "valor_texto", "valor_numero", "valor_booleano",
    })

    @classmethod
    def list_for(cls, id_pedido: int, posicion_linea: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} "
                f"WHERE id_pedido=%s AND posicion_linea=%s ORDER BY ruta",
                (int(id_pedido), int(posicion_linea)),
            )
            return list(cur.fetchall())

    @classmethod
    def replace_for_line(
        cls, id_pedido: int, posicion_linea: int, usos: list[dict[str, Any]]
    ) -> None:
        """
        Cada uso debe tener:
          ruta, tipo_valor ∈ {'texto','numero','booleano','nulo'}
          valor_texto / valor_numero / valor_booleano según tipo.
        """
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} "
                f"WHERE id_pedido=%s AND posicion_linea=%s",
                (int(id_pedido), int(posicion_linea)),
            )
            for uso in usos:
                ruta = str(uso.get("ruta") or "").strip()
                tipo = str(uso.get("tipo_valor") or "").strip().lower()
                if not ruta or tipo not in {"texto", "numero", "booleano", "nulo"}:
                    continue
                cur.execute(
                    f"INSERT INTO {cls.table} "
                    "(id_pedido, posicion_linea, ruta, tipo_valor, "
                    " valor_texto, valor_numero, valor_booleano) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (
                        int(id_pedido), int(posicion_linea), ruta, tipo,
                        uso.get("valor_texto") if tipo == "texto" else None,
                        uso.get("valor_numero") if tipo == "numero" else None,
                        uso.get("valor_booleano") if tipo == "booleano" else None,
                    ),
                )