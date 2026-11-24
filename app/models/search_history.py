# app/models/search_history.py
"""SearchHistoryModel relacional (Fase 6). Historial de búsquedas."""
from __future__ import annotations

from typing import Any

from app.repositories.historial_busqueda import (
    HistorialBusquedaRepository,
    BusquedasRecomendacionRepository,
    EnviosRecomendacionRepository,
)


class SearchHistoryModel:
    @classmethod
    def get_or_create_for_usuario(cls, id_usuario: int) -> int:
        row = HistorialBusquedaRepository.get_by_usuario(id_usuario)
        if row:
            return row["id_historial"]
        return HistorialBusquedaRepository.create_for_usuario(id_usuario)["id_historial"]

    @classmethod
    def register_search(
        cls, id_usuario: int, *, termino: str, consulta: str | None = None
    ) -> dict[str, Any]:
        id_historial = cls.get_or_create_for_usuario(id_usuario)
        return BusquedasRecomendacionRepository.register_search(
            id_historial=id_historial, termino=termino, consulta=consulta
        )

    @classmethod
    def record_envio(cls, id_usuario: int, identificador_envio: str) -> dict[str, Any]:
        id_historial = cls.get_or_create_for_usuario(id_usuario)
        return EnviosRecomendacionRepository.append(id_historial, identificador_envio)

    @classmethod
    def get_full(cls, id_usuario: int) -> dict[str, Any]:
        row = HistorialBusquedaRepository.get_by_usuario(id_usuario)
        if not row:
            return {"id_historial": None, "busquedas": [], "envios": []}
        ih = row["id_historial"]
        return {
            "id_historial": ih,
            "busquedas": BusquedasRecomendacionRepository.list_for(ih),
            "envios": EnviosRecomendacionRepository.list_for(ih),
        }