# app/models/feedback.py
"""FeedbackModel relacional (Fase 6). Feedback de recomendación."""
from __future__ import annotations

from typing import Any

from app.repositories.feedback_recomendacion import (
    FeedbackRecomendacionRepository,
    FeedbackRecomendacionItemsRepository,
    FeedbackRecomendacionRecientesRepository,
    FeedbackRecomendacionSenalesRepository,
)


class FeedbackModel:
    @classmethod
    def create_empty(cls) -> int:
        return FeedbackRecomendacionRepository.create_empty()["id_feedback"]

    @classmethod
    def record_interaction(
        cls,
        id_feedback: int,
        *,
        entidad_clave: str,
        interaccion: str,
        tipo_entidad: str | None = None,
        id_entidad: int | None = None,
    ) -> dict[str, Any]:
        return FeedbackRecomendacionItemsRepository.upsert(
            id_feedback=id_feedback,
            entidad_clave=entidad_clave,
            interaccion=interaccion,
            tipo_entidad=tipo_entidad,
            id_entidad=id_entidad,
        )

    @classmethod
    def record_view(cls, id_feedback: int, entidad_clave: str) -> dict[str, Any]:
        return FeedbackRecomendacionSenalesRepository.record_view(
            id_feedback=id_feedback, entidad_clave=entidad_clave
        )

    @classmethod
    def set_recientes(cls, id_feedback: int, entidades: list[str]) -> None:
        FeedbackRecomendacionRecientesRepository.replace_for(id_feedback, entidades)

    @classmethod
    def get_full(cls, id_feedback: int) -> dict[str, Any]:
        return {
            "items": FeedbackRecomendacionItemsRepository.list_for(id_feedback),
            "recientes": FeedbackRecomendacionRecientesRepository.list_for(id_feedback),
            "senales": FeedbackRecomendacionSenalesRepository.list_for(id_feedback),
        }