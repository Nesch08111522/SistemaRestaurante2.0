# app/repositories/pedidos_mercado.py
"""
Repositorio de public.pedidos_mercado.
Columnas del .sql:
  id_pedido, id_restaurante, id_usuario, dia, horario_entrega,
  pagado, estado, total, metodo_pago, canal, creado_en,
  nombre_negocio_snapshot, descuento, reembolsado,
  semilla_prueba, clave_solicitud
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class PedidosMercadoRepository(PostgresRepository):
    table = "public.pedidos_mercado"
    columns = frozenset({
        "id_pedido", "id_restaurante", "id_usuario", "dia",
        "horario_entrega", "pagado", "estado", "total",
        "metodo_pago", "canal", "creado_en", "nombre_negocio_snapshot",
        "descuento", "reembolsado", "semilla_prueba", "clave_solicitud",
    })

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_pedido=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def get_by_clave_solicitud(cls, clave: str) -> dict[str, Any] | None:
        """Idempotencia: misma clave de solicitud = un solo pedido."""
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE clave_solicitud=%s",
                (clave,),
            )
            return cur.fetchone()

    @classmethod
    def list_by_usuario(
        cls, id_usuario: int, *, limit: int = 50
    ) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_usuario=%s "
                f"ORDER BY creado_en DESC LIMIT %s",
                (int(id_usuario), int(limit)),
            )
            return list(cur.fetchall())

    @classmethod
    def list_by_restaurante(
        cls,
        id_restaurante: int,
        *,
        estado: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        where = ""
        params: list[Any] = [int(id_restaurante)]
        if estado:
            where = "AND estado=%s"
            params.append(estado)
        params.append(int(limit))
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_restaurante=%s {where} "
                f"ORDER BY creado_en DESC LIMIT %s",
                tuple(params),
            )
            return list(cur.fetchall())

    @classmethod
    def insert(
        cls,
        *,
        id_restaurante: int,
        id_usuario: int,
        dia: date,
        estado: str,
        total: float,
        nombre_negocio_snapshot: str | None = None,
        horario_entrega: datetime | None = None,
        metodo_pago: str | None = None,
        canal: str | None = None,
        descuento: float = 0,
        clave_solicitud: str | None = None,
        pagado: bool = False,
        semilla_prueba: str | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.table}
                    (id_restaurante, id_usuario, dia, horario_entrega,
                     pagado, estado, total, metodo_pago, canal, creado_en,
                     nombre_negocio_snapshot, descuento, reembolsado,
                     semilla_prueba, clave_solicitud)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,FALSE,%s,%s)
                RETURNING *
                """,
                (
                    int(id_restaurante), int(id_usuario), dia, horario_entrega,
                    bool(pagado), estado.strip(), float(total),
                    metodo_pago, canal, now, nombre_negocio_snapshot,
                    float(descuento), semilla_prueba, clave_solicitud,
                ),
            )
            return cur.fetchone()

    @classmethod
    def update_fields(cls, id_pedido: int, values: dict[str, Any]) -> dict[str, Any] | None:
        allowed = cls.columns - {"id_pedido", "id_usuario", "id_restaurante", "creado_en"}
        payload = {k: v for k, v in values.items() if k in allowed}
        if not payload:
            return cls.get_by_id(id_pedido)
        names = list(payload)
        assignments = ",".join(f"{name}=%s" for name in names)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} SET {assignments} "
                f"WHERE id_pedido=%s RETURNING *",
                tuple(payload[name] for name in names) + (int(id_pedido),),
            )
            return cur.fetchone()

    @classmethod
    def mark_paid(cls, id_pedido: int) -> dict[str, Any] | None:
        return cls.update_fields(id_pedido, {"pagado": True})

    @classmethod
    def mark_refunded(cls, id_pedido: int) -> dict[str, Any] | None:
        return cls.update_fields(id_pedido, {"reembolsado": True})