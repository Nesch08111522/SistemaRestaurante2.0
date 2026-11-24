# app/models/food_group.py
"""FoodGroupModel relacional (Fase 7). Grupos de comida."""
from __future__ import annotations

from typing import Any

from app.repositories.grupos_comida import (
    GruposComidaRepository,
    GruposComidaMiembrosRepository,
    GruposComidaPreferenciasRepository,
    GruposComidaPreferenciasEvitarRepository,
    GruposComidaVotosRepository,
)


class FoodGroupModel:
    @classmethod
    def get_by_id(cls, id_grupo: int, *, full: bool = True) -> dict[str, Any] | None:
        row = GruposComidaRepository.get_by_id(id_grupo)
        if not row:
            return None
        if not full:
            return row
        return cls._enrich(row)

    @classmethod
    def _enrich(cls, row: dict[str, Any]) -> dict[str, Any]:
        gid = row["id_grupo"]
        miembros = GruposComidaMiembrosRepository.list_for(gid)
        for m in miembros:
            m["presupuesto"] = (
                GruposComidaPreferenciasRepository.get_for(gid, m["id_usuario"]) or {}
            ).get("presupuesto")
            m["evitar"] = GruposComidaPreferenciasEvitarRepository.list_for(
                gid, m["id_usuario"]
            )
        return {
            **row,
            "miembros": miembros,
            "votos": GruposComidaVotosRepository.list_for(gid),
        }

    @classmethod
    def create(
        cls,
        *,
        id_anfitrion: int,
        titulo: str,
        invitacion: str,
        vence_en=None,
    ) -> dict[str, Any]:
        grupo = GruposComidaRepository.insert(
            id_anfitrion=id_anfitrion,
            titulo=titulo,
            invitacion=invitacion,
            vence_en=vence_en,
        )
        GruposComidaMiembrosRepository.add(
            grupo["id_grupo"], id_anfitrion, es_anfitrion=True
        )
        return cls.get_by_id(grupo["id_grupo"], full=True)

    @classmethod
    def join(cls, id_grupo: int, id_usuario: int) -> None:
        GruposComidaMiembrosRepository.add(id_grupo, id_usuario, es_anfitrion=False)

    @classmethod
    def set_preferences(
        cls,
        id_grupo: int,
        id_usuario: int,
        *,
        presupuesto: float | None = None,
        evitar: list[str] | None = None,
    ) -> None:
        GruposComidaPreferenciasRepository.upsert(
            id_grupo, id_usuario, presupuesto=presupuesto
        )
        if evitar is not None:
            GruposComidaPreferenciasEvitarRepository.replace_for(
                id_grupo, id_usuario, evitar
            )

    @classmethod
    def vote(cls, id_grupo: int, id_usuario: int, id_restaurante: int) -> dict[str, Any]:
        return GruposComidaVotosRepository.vote(id_grupo, id_usuario, id_restaurante)