# app/models/market_kitchen.py
"""MarketKitchenModel relacional (Fase 7). Cocinas de mercado."""
from __future__ import annotations

from typing import Any

from app.repositories.cocinas_mercado import (
    CocinasMercadoRepository,
    CocinasMercadoEquipoRepository,
    CocinasMercadoZonasRepository,
    CocinasMercadoCanalesRepository,
    CocinasMercadoDespensaRepository,
)


class MarketKitchenModel:
    @classmethod
    def get_by_id(cls, id_cocina: int, *, full: bool = True) -> dict[str, Any] | None:
        row = CocinasMercadoRepository.get_by_id(id_cocina)
        if not row:
            return None
        if not full:
            return row
        return cls._enrich(row)

    @classmethod
    def _enrich(cls, row: dict[str, Any]) -> dict[str, Any]:
        cid = row["id_cocina"]
        return {
            **row,
            "equipo": CocinasMercadoEquipoRepository.list_for(cid),
            "zonas": CocinasMercadoZonasRepository.list_for(cid),
            "canales": CocinasMercadoCanalesRepository.list_for(cid),
            "despensa": CocinasMercadoDespensaRepository.list_for(cid),
        }

    @classmethod
    def list_all(cls) -> list[dict[str, Any]]:
        return CocinasMercadoRepository.list_all()

    @classmethod
    def create(
        cls,
        *,
        tipo: str,
        id_lider: int | None = None,
        equipo: list[int] | None = None,
        zonas: list[str] | None = None,
        canales: list[str] | None = None,
        **extra,
    ) -> dict[str, Any]:
        cocina = CocinasMercadoRepository.insert(
            tipo=tipo, id_lider=id_lider, **extra
        )
        cid = cocina["id_cocina"]
        if equipo:
            CocinasMercadoEquipoRepository.replace_for(cid, equipo)
        if zonas:
            CocinasMercadoZonasRepository.replace_for(cid, zonas)
        if canales:
            CocinasMercadoCanalesRepository.replace_for(cid, canales)
        return cls.get_by_id(cid, full=True)