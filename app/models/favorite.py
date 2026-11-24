# app/models/favorite.py
"""FavoriteModel relacional (Fase 4). Fachada de favoritos."""
from __future__ import annotations

from typing import Any

from app.repositories.favoritos import FavoritosRepository


class FavoriteModel:
    @classmethod
    def list_by_usuario(cls, id_usuario: int) -> list[dict[str, Any]]:
        return FavoritosRepository.list_by_usuario(id_usuario)

    @classmethod
    def add(cls, id_usuario: int, id_restaurante: int) -> dict[str, Any]:
        return FavoritosRepository.add(id_usuario, id_restaurante)

    @classmethod
    def remove(cls, id_usuario: int, id_restaurante: int) -> bool:
        return FavoritosRepository.remove(id_usuario, id_restaurante)

    @classmethod
    def toggle(cls, id_usuario: int, id_restaurante: int) -> bool:
        """Devuelve True si ahora es favorito, False si se quitó."""
        if FavoritosRepository.exists(id_usuario, id_restaurante):
            FavoritosRepository.remove(id_usuario, id_restaurante)
            return False
        FavoritosRepository.add(id_usuario, id_restaurante)
        return True

    @classmethod
    def is_favorite(cls, id_usuario: int, id_restaurante: int) -> bool:
        return FavoritosRepository.exists(id_usuario, id_restaurante)