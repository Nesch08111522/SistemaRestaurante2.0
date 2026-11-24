# app/models/promotion.py
"""PromotionModel relacional (Fase 4). Fachada de promociones."""
from __future__ import annotations

from typing import Any

from app.repositories.promociones import PromocionesRepository


class PromotionModel:
    @classmethod
    def get_by_id(cls, id_promocion: int) -> dict[str, Any] | None:
        return PromocionesRepository.get_by_id(id_promocion)

    @classmethod
    def list_by_restaurante(
        cls, id_restaurante: int, *, vigentes: bool = False
    ) -> list[dict[str, Any]]:
        return PromocionesRepository.list_by_restaurante(
            id_restaurante, vigentes=vigentes
        )

    @classmethod
    def create(
        cls,
        *,
        id_restaurante: int,
        descripcion: str,
        valida_hasta=None,
        porcentaje_descuento: float | None = None,
    ) -> dict[str, Any]:
        return PromocionesRepository.insert(
            id_restaurante=id_restaurante,
            descripcion=descripcion,
            valida_hasta=valida_hasta,
            porcentaje_descuento=porcentaje_descuento,
        )

    @classmethod
    def update(cls, id_promocion: int, values: dict[str, Any]) -> dict[str, Any] | None:
        return PromocionesRepository.update_fields(id_promocion, values)