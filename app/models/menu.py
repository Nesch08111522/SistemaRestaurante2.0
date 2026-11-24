# app/models/menu.py
"""MenuModel relacional (Fase 4). Fachada de menús diarios."""
from __future__ import annotations

from typing import Any

from app.repositories.menus_diarios import (
    MenusDiariosRepository,
    MenusDiariosPlatosRepository,
    MenusDiariosEspecialesRepository,
)


class MenuModel:
    @classmethod
    def get_by_id(cls, id_menu: int, *, full: bool = True) -> dict[str, Any] | None:
        row = MenusDiariosRepository.get_by_id(id_menu)
        if not row:
            return None
        if not full:
            return row
        return cls._enrich(row)

    @classmethod
    def _enrich(cls, row: dict[str, Any]) -> dict[str, Any]:
        mid = row["id_menu"]
        return {
            **row,
            "platos": MenusDiariosPlatosRepository.list_for(mid),
            "especiales": MenusDiariosEspecialesRepository.list_for(mid),
        }

    @classmethod
    def list_by_restaurante(
        cls, id_restaurante: int, *, full: bool = False, only_active: bool = True
    ) -> list[dict[str, Any]]:
        rows = MenusDiariosRepository.list_by_restaurante(
            id_restaurante, only_active=only_active
        )
        if not full:
            return rows
        return [cls._enrich(r) for r in rows]

    @classmethod
    def create(
        cls,
        *,
        id_restaurante: int,
        fecha,
        tipo: str,
        precio: float = 0,
        dia_semana: str | None = None,
        platos: list[dict[str, Any]] | None = None,
        especiales: list[str] | None = None,
    ) -> dict[str, Any]:
        menu = MenusDiariosRepository.insert(
            id_restaurante=id_restaurante,
            fecha=fecha,
            tipo=tipo,
            precio=precio,
            dia_semana=dia_semana,
        )
        if platos:
            MenusDiariosPlatosRepository.replace_for(menu["id_menu"], platos)
        if especiales:
            MenusDiariosEspecialesRepository.replace_for(menu["id_menu"], especiales)
        return cls.get_by_id(menu["id_menu"], full=True)