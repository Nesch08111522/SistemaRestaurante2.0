# app/models/notification.py
"""NotificationModel relacional (Fase 4). Fachada de notificaciones."""
from __future__ import annotations

from typing import Any

from app.repositories.notificaciones import NotificacionesRepository


class NotificationModel:
    @classmethod
    def list_by_usuario(
        cls, id_usuario: int, *, only_unread: bool = False, limit: int = 50
    ) -> list[dict[str, Any]]:
        return NotificacionesRepository.list_by_usuario(
            id_usuario, only_unread=only_unread, limit=limit
        )

    @classmethod
    def notify(
        cls,
        ids_usuarios: list[int],
        titulo: str,
        mensaje: str,
        *,
        tipo: str = "info",
        enlace: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Envía una notificación a varios usuarios.
        Reemplaza a `notify()` del proyecto viejo.
        """
        if not ids_usuarios:
            return []
        return NotificacionesRepository.insert_many(
            ids_usuarios=ids_usuarios,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            enlace=enlace,
        )

    @classmethod
    def mark_read(cls, id_notificacion: int) -> dict[str, Any] | None:
        return NotificacionesRepository.mark_read(id_notificacion)

    @classmethod
    def mark_all_read(cls, id_usuario: int) -> int:
        return NotificacionesRepository.mark_all_read(id_usuario)

    @classmethod
    def count_unread(cls, id_usuario: int) -> int:
        return NotificacionesRepository.count_unread(id_usuario)