# app/models/audit.py
"""AuditModel relacional (Fase 7). Auditoría de eventos."""
from __future__ import annotations

from typing import Any

from app.repositories.auditoria import (
    EventosAuditoriaRepository,
    EventosAuditoriaAtributosRepository,
)


class AuditModel:
    @classmethod
    def record(
        cls,
        *,
        accion: str,
        tipo_recurso: str,
        id_usuario_actor: int | None = None,
        id_empresa: int | None = None,
        id_recurso: str | None = None,
        id_solicitud: str | None = None,
        hash_ip: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Registra un evento de auditoría. `metadata` se traduce a atributos
        (aplanados como `clave.subclave[i]`).
        """
        atributos = cls._flatten_metadata(metadata) if metadata else None
        return EventosAuditoriaRepository.record(
            accion=accion,
            tipo_recurso=tipo_recurso,
            id_usuario_actor=id_usuario_actor,
            id_empresa=id_empresa,
            id_recurso=id_recurso,
            id_solicitud=id_solicitud,
            hash_ip=hash_ip,
            atributos=atributos,
        )

    @staticmethod
    def _flatten_metadata(metadata: dict[str, Any]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        def walk(prefix: str, value: Any):
            if isinstance(value, dict):
                for k, v in value.items():
                    walk(f"{prefix}.{k}" if prefix else str(k), v)
            elif isinstance(value, list):
                for idx, v in enumerate(value):
                    walk(f"{prefix}[{idx}]", v)
            elif isinstance(value, bool):
                out.append({"ruta": prefix, "tipo_valor": "booleano", "valor_booleano": value})
            elif isinstance(value, (int, float)):
                out.append({"ruta": prefix, "tipo_valor": "numero", "valor_numero": value})
            elif value is None:
                out.append({"ruta": prefix, "tipo_valor": "nulo"})
            else:
                out.append({"ruta": prefix, "tipo_valor": "texto", "valor_texto": str(value)})
        walk("", metadata)
        return out

    @classmethod
    def get_full(cls, id_evento: int) -> dict[str, Any] | None:
        row = EventosAuditoriaRepository.get_by_id(id_evento)
        if not row:
            return None
        return {
            **row,
            "atributos": EventosAuditoriaAtributosRepository.list_for(id_evento),
        }

    @classmethod
    def list_by_actor(
        cls, id_usuario_actor: int, *, limit: int = 100
    ) -> list[dict[str, Any]]:
        return EventosAuditoriaRepository.list_by_actor(
            id_usuario_actor, limit=limit
        )