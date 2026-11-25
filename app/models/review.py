# app/models/review.py
"""ReviewModel relacional (Fase 4). Fachada de reseñas."""
from __future__ import annotations

from typing import Any

from app.repositories.resenas import ResenasRepository


class ReviewModel:
    @classmethod
    def get_by_id(cls, id_resena: int) -> dict[str, Any] | None:
        return ResenasRepository.get_by_id(id_resena)

    @classmethod
    def list_by_restaurante(
        cls, id_restaurante: int, *, limit: int = 100
    ) -> list[dict[str, Any]]:
        return ResenasRepository.list_by_restaurante(id_restaurante, limit=limit)

    @classmethod
    def list_by_usuario(
        cls, id_usuario: int, *, limit: int = 100
    ) -> list[dict[str, Any]]:
        return ResenasRepository.list_by_usuario(id_usuario, limit=limit)

    @classmethod
    def create(
        cls,
        *,
        id_restaurante: int,
        id_usuario: int,
        calificacion: int,
        comentario: str | None = None,
    ) -> dict[str, Any]:
        return ResenasRepository.insert(
            id_restaurante=id_restaurante,
            id_usuario=id_usuario,
            calificacion=calificacion,
            comentario=comentario,
        )

    @classmethod
    def summary(cls, id_restaurante: int) -> dict[str, Any]:
        return ResenasRepository.average_for_restaurante(id_restaurante)