# app/models/moderation.py
"""ModerationModel relacional (Fase 6). Fachada de moderaciones."""
from __future__ import annotations

from typing import Any

from app.repositories.moderaciones import (
    ModeracionesRepository,
    ModeracionesBanderasRepository,
    ModeracionesHistorialEstadosRepository,
    ModeracionesContenidoAtributosRepository,
    ModeracionesEvaluacionesIARepository,
    ModeracionesEvaluacionesIAAtributosRepository,
)


class ModerationModel:
    @classmethod
    def get_by_id(cls, id_moderacion: int, *, full: bool = True) -> dict[str, Any] | None:
        row = ModeracionesRepository.get_by_id(id_moderacion)
        if not row:
            return None
        if not full:
            return row
        return cls._enrich(row)

    @classmethod
    def _enrich(cls, row: dict[str, Any]) -> dict[str, Any]:
        mid = row["id_moderacion"]
        return {
            **row,
            "banderas": ModeracionesBanderasRepository.list_for(mid),
            "historial": ModeracionesHistorialEstadosRepository.list_for(mid),
            "contenido_atributos": ModeracionesContenidoAtributosRepository.list_for(mid),
            "evaluacion_ia": ModeracionesEvaluacionesIARepository.get_for(mid),
            "evaluacion_ia_atributos": ModeracionesEvaluacionesIAAtributosRepository.list_for(mid),
        }

    @classmethod
    def create(
        cls,
        *,
        tipo_contenido: str,
        id_contenido: int | None = None,
        id_usuario: int | None = None,
        estado: str | None = None,
        motivo: str | None = None,
        marcado: bool = False,
        banderas: list[str] | None = None,
        contenido_atributos: list[dict[str, Any]] | None = None,
        evaluacion_ia: dict[str, Any] | None = None,
        evaluacion_ia_atributos: list[dict[str, Any]] | None = None,
        estado_inicial_historial: str | None = None,
    ) -> dict[str, Any]:
        row = ModeracionesRepository.insert(
            tipo_contenido=tipo_contenido,
            id_contenido=id_contenido,
            id_usuario=id_usuario,
            estado=estado,
            motivo=motivo,
            marcado=marcado,
        )
        mid = row["id_moderacion"]

        if banderas:
            ModeracionesBanderasRepository.replace_for(mid, banderas)
        if contenido_atributos:
            ModeracionesContenidoAtributosRepository.replace_for(mid, contenido_atributos)
        if evaluacion_ia:
            ModeracionesEvaluacionesIARepository.upsert_for(mid, **evaluacion_ia)
        if evaluacion_ia_atributos:
            ModeracionesEvaluacionesIAAtributosRepository.replace_for(
                mid, evaluacion_ia_atributos
            )
        if estado_inicial_historial or estado:
            ModeracionesHistorialEstadosRepository.append(
                mid,
                estado_nuevo=estado_inicial_historial or estado or "pending",
                origen="creacion",
            )
        return cls.get_by_id(mid, full=True)

    @classmethod
    def transition(
        cls,
        id_moderacion: int,
        *,
        nuevo_estado: str,
        id_usuario_actor: int | None = None,
        notas: str | None = None,
    ) -> dict[str, Any] | None:
        actual = ModeracionesRepository.get_by_id(id_moderacion)
        if not actual:
            return None
        ModeracionesRepository.update_fields(
            id_moderacion,
            {"estado": nuevo_estado, "id_decisor_humano": id_usuario_actor},
        )
        ModeracionesHistorialEstadosRepository.append(
            id_moderacion,
            estado_nuevo=nuevo_estado,
            estado_anterior=actual.get("estado"),
            origen="manual",
            notas=notas,
            id_usuario_actor=id_usuario_actor,
        )
        return cls.get_by_id(id_moderacion, full=True)

    @classmethod
    def list_by_estado(cls, estado: str, *, limit: int = 100) -> list[dict[str, Any]]:
        return ModeracionesRepository.list_by_estado(estado, limit=limit)