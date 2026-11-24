# app/models/restaurant.py
"""
RestaurantModel relacional (Fase 3).

Ensambla un restaurante con sus tablas hijas y sus platos.
"""
from __future__ import annotations

from typing import Any

from app.repositories.restaurantes import (
    RestaurantesRepository,
    RestaurantesEtiquetasRepository,
    RestaurantesCaracteristicasRepository,
    RestaurantesRestriccionesDieteticasRepository,
    RestaurantesCanalesMercadoRepository,
)
from app.repositories.platos import PlatosRepository
from app.repositories.restaurantes_platos import RestaurantesPlatosRepository


class RestaurantModel:
    """Fachada de restaurantes."""

    @classmethod
    def get_by_id(cls, id_restaurante: int, *, full: bool = True) -> dict[str, Any] | None:
        row = RestaurantesRepository.get_by_id(id_restaurante)
        if not row:
            return None
        if not full:
            return row
        return cls._enrich(row)

    @classmethod
    def _enrich(cls, row: dict[str, Any]) -> dict[str, Any]:
        rid = row["id_restaurante"]
        platos_ids = RestaurantesPlatosRepository.list_plato_ids(rid)
        platos = []
        for pid in platos_ids:
            plato = PlatosRepository.get_by_id(pid)
            if plato:
                platos.append(plato)

        return {
            **row,
            "etiquetas": RestaurantesEtiquetasRepository.list_for(rid),
            "caracteristicas": RestaurantesCaracteristicasRepository.list_for(rid),
            "restricciones_dieteticas": RestaurantesRestriccionesDieteticasRepository.list_for(rid),
            "canales_mercado": RestaurantesCanalesMercadoRepository.list_for(rid),
            "platos": platos,
        }

    @classmethod
    def list_by_empresa(cls, id_empresa: int, *, full: bool = False) -> list[dict[str, Any]]:
        rows = RestaurantesRepository.list_by_empresa(id_empresa)
        if not full:
            return rows
        return [cls._enrich(row) for row in rows]

    @classmethod
    def list_published(cls, *, limit: int = 100) -> list[dict[str, Any]]:
        return RestaurantesRepository.list_published(limit=limit)

    @classmethod
    def is_owner(cls, user_id: int, id_restaurante: int) -> bool:
        row = RestaurantesRepository.get_by_id(id_restaurante)
        return bool(row and row.get("id_propietario") == user_id)

    @classmethod
    def get_full_menu(cls, id_restaurante: int) -> list[dict[str, Any]]:
        """Devuelve los platos del restaurante con sus hijas."""
        from app.repositories.platos import (
            PlatosEtiquetasRepository,
            PlatosIngredientesRepository,
            PlatosRestriccionesDieteticasRepository,
            PlatosInformacionNutricionalRepository,
        )
        platos_ids = RestaurantesPlatosRepository.list_plato_ids(id_restaurante)
        resultado = []
        for pid in platos_ids:
            plato = PlatosRepository.get_by_id(pid)
            if not plato:
                continue
            resultado.append({
                **plato,
                "etiquetas": PlatosEtiquetasRepository.list_for(pid),
                "ingredientes": PlatosIngredientesRepository.list_for(pid),
                "restricciones_dieteticas": PlatosRestriccionesDieteticasRepository.list_for(pid),
                "info_nutricional": PlatosInformacionNutricionalRepository.get_for(pid),
            })
        return resultado