# app/models/discovery.py
"""DiscoveryModel relacional (Fase 7). Radar de negocios."""
from __future__ import annotations

from typing import Any

from app.repositories.descubrimiento import (
    FuentesDescubrimientoRepository,
    EjecucionesDescubrimientoRepository,
)
from app.repositories.consultas_comerciales import ConsultasComercialesRepository


class DiscoveryModel:
    @classmethod
    def list_sources(cls) -> list[dict[str, Any]]:
        return FuentesDescubrimientoRepository.list_enabled()

    @classmethod
    def list_due(cls, *, limit: int = 50) -> list[dict[str, Any]]:
        return FuentesDescubrimientoRepository.list_due(limit=limit)

    @classmethod
    def run_source(
        cls,
        *,
        id_fuente: int,
        nombre_fuente: str,
        id_usuario_actor: int | None = None,
    ) -> dict[str, Any]:
        ejec = EjecucionesDescubrimientoRepository.start(
            id_fuente=id_fuente,
            nombre_fuente_snapshot=nombre_fuente,
            id_usuario_actor=id_usuario_actor,
        )
        return ejec

    @classmethod
    def finish_run(
        cls,
        id_ejecucion: int,
        *,
        estado: str,
        tipo_error: str | None = None,
        mensaje_error: str | None = None,
        id_fuente: int | None = None,
    ) -> dict[str, Any] | None:
        result = EjecucionesDescubrimientoRepository.finish(
            id_ejecucion, estado=estado,
            tipo_error=tipo_error, mensaje_error=mensaje_error,
        )
        if id_fuente and estado == "ok":
            FuentesDescubrimientoRepository.mark_run(id_fuente)
        elif id_fuente and estado != "ok":
            FuentesDescubrimientoRepository.mark_run(
                id_fuente, error=mensaje_error or tipo_error
            )
        return result

    @classmethod
    def register_query(
        cls,
        *,
        id_usuario_actor: int | None,
        estado: str,
        radio_km: float | None = None,
        latitud: float | None = None,
        longitud: float | None = None,
    ) -> dict[str, Any]:
        return ConsultasComercialesRepository.register(
            id_usuario_actor=id_usuario_actor,
            estado=estado,
            radio_km=radio_km,
            latitud=latitud,
            longitud=longitud,
        )