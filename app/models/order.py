# app/models/order.py
"""
OrderModel relacional (Fase 5). Fachada de pedidos del mercado.

Ensambla:
  - cabecera (pedidos_mercado)
  - líneas (pedidos_mercado_lineas) + adicionales + usos
  - historial (pedidos_mercado_historial_estados)
  - destino (pedidos_mercado_destinos)
"""
from __future__ import annotations

from datetime import date
from typing import Any

from app.db.repository import shared_transaction
from app.repositories.pedidos_mercado import PedidosMercadoRepository
from app.repositories.pedidos_mercado_lineas import (
    PedidosMercadoLineasRepository,
    PedidosMercadoLineasAdicionalesRepository,
    PedidosMercadoLineasUsosRepository,
)
from app.repositories.pedidos_mercado_historial import (
    PedidosMercadoHistorialRepository,
)
from app.repositories.pedidos_mercado_destinos import (
    PedidosMercadoDestinosRepository,
)


class OrderModel:
    # ---------- lectura ----------

    @classmethod
    def get_by_id(cls, id_pedido: int, *, full: bool = True) -> dict[str, Any] | None:
        row = PedidosMercadoRepository.get_by_id(id_pedido)
        if not row:
            return None
        if not full:
            return row
        return cls._enrich(row)

    @classmethod
    def _enrich(cls, row: dict[str, Any]) -> dict[str, Any]:
        pid = row["id_pedido"]
        lineas = PedidosMercadoLineasRepository.list_for(pid)
        for linea in lineas:
            pos = linea["posicion"]
            linea["adicionales"] = (
                PedidosMercadoLineasAdicionalesRepository.list_for(pid, pos)
            )
            linea["usos"] = PedidosMercadoLineasUsosRepository.list_for(pid, pos)
        return {
            **row,
            "lineas": lineas,
            "historial": PedidosMercadoHistorialRepository.list_for(pid),
            "destino": PedidosMercadoDestinosRepository.get_for(pid),
        }

    @classmethod
    def list_by_usuario(
        cls, id_usuario: int, *, limit: int = 50, full: bool = False
    ) -> list[dict[str, Any]]:
        rows = PedidosMercadoRepository.list_by_usuario(id_usuario, limit=limit)
        if not full:
            return rows
        return [cls._enrich(r) for r in rows]

    @classmethod
    def list_by_restaurante(
        cls,
        id_restaurante: int,
        *,
        estado: str | None = None,
        limit: int = 100,
        full: bool = False,
    ) -> list[dict[str, Any]]:
        rows = PedidosMercadoRepository.list_by_restaurante(
            id_restaurante, estado=estado, limit=limit
        )
        if not full:
            return rows
        return [cls._enrich(r) for r in rows]

    # ---------- creación ----------

    @classmethod
    def create(
        cls,
        *,
        id_restaurante: int,
        id_usuario: int,
        dia: date,
        estado: str = "pending",
        total: float = 0,
        nombre_negocio_snapshot: str | None = None,
        horario_entrega=None,
        metodo_pago: str | None = None,
        canal: str | None = None,
        descuento: float = 0,
        clave_solicitud: str | None = None,
        pagado: bool = False,
        semilla_prueba: str | None = None,
        lineas: list[dict[str, Any]] | None = None,
        destino: dict[str, Any] | None = None,
        estado_inicial_historial: str | None = None,
    ) -> dict[str, Any]:
        """
        Crea un pedido completo en una sola transacción.

        Cada línea: {nombre_snapshot, cantidad, precio_unitario,
                     id_plato?, id_oferta?, costo?, ahorro?,
                     adicionales?: [str], usos?: [dict]}
        Destino: {destinatario?, telefono?, direccion?, distrito?,
                  ciudad?, referencia?, latitud?, longitud?}
        """
        # Idempotencia: si ya existe con la misma clave, lo devolvemos.
        if clave_solicitud:
            existente = PedidosMercadoRepository.get_by_clave_solicitud(clave_solicitud)
            if existente:
                return cls.get_by_id(existente["id_pedido"], full=True)

        with shared_transaction():
            cab = PedidosMercadoRepository.insert(
                id_restaurante=id_restaurante,
                id_usuario=id_usuario,
                dia=dia,
                estado=estado,
                total=total,
                nombre_negocio_snapshot=nombre_negocio_snapshot,
                horario_entrega=horario_entrega,
                metodo_pago=metodo_pago,
                canal=canal,
                descuento=descuento,
                clave_solicitud=clave_solicitud,
                pagado=pagado,
                semilla_prueba=semilla_prueba,
            )
            pid = cab["id_pedido"]

            for idx, linea in enumerate(lineas or [], start=1):
                stored = PedidosMercadoLineasRepository.insert_line(
                    id_pedido=pid,
                    posicion=idx,
                    nombre_snapshot=linea["nombre_snapshot"],
                    cantidad=linea["cantidad"],
                    precio_unitario=linea["precio_unitario"],
                    id_plato=linea.get("id_plato"),
                    id_oferta=linea.get("id_oferta"),
                    costo=linea.get("costo"),
                    ahorro=linea.get("ahorro", 0),
                )
                pos = stored["posicion"]
                if linea.get("adicionales"):
                    PedidosMercadoLineasAdicionalesRepository.replace_for_line(
                        pid, pos, linea["adicionales"]
                    )
                if linea.get("usos"):
                    PedidosMercadoLineasUsosRepository.replace_for_line(
                        pid, pos, linea["usos"]
                    )

            if destino:
                PedidosMercadoDestinosRepository.upsert_for(id_pedido=pid, **destino)

            # Historial inicial
            PedidosMercadoHistorialRepository.append(
                pid, estado_inicial_historial or estado
            )

        return cls.get_by_id(pid, full=True)

    # ---------- transiciones de estado ----------

    @classmethod
    def change_status(
        cls, id_pedido: int, nuevo_estado: str
    ) -> dict[str, Any] | None:
        with shared_transaction():
            actualizado = PedidosMercadoRepository.update_fields(
                id_pedido, {"estado": nuevo_estado}
            )
            if not actualizado:
                return None
            PedidosMercadoHistorialRepository.append(id_pedido, nuevo_estado)
        return cls.get_by_id(id_pedido, full=True)

    @classmethod
    def mark_paid(cls, id_pedido: int) -> dict[str, Any] | None:
        return PedidosMercadoRepository.mark_paid(id_pedido)

    @classmethod
    def mark_refunded(cls, id_pedido: int) -> dict[str, Any] | None:
        return PedidosMercadoRepository.mark_refunded(id_pedido)