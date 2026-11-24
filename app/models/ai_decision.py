# app/models/ai_decision.py
"""AIDecisionModel relacional (Fase 6). Registro de decisiones de IA."""
from __future__ import annotations

from hashlib import sha256
from typing import Any

from app.repositories.decisiones_ia import (
    DecisionesIARepository,
    DecisionesIAAtributosRepository,
)


class AIDecisionModel:
    @classmethod
    def get_by_id(cls, id_decision: int) -> dict[str, Any] | None:
        row = DecisionesIARepository.get_by_id(id_decision)
        if not row:
            return None
        return {
            **row,
            "entrada": DecisionesIAAtributosRepository.list_for(id_decision, "entrada"),
            "salida": DecisionesIAAtributosRepository.list_for(id_decision, "salida"),
        }

    @classmethod
    def record(
        cls,
        *,
        tipo: str,
        entidad: str,
        id_usuario_actor: int,
        payload_entrada: dict[str, Any] | str | None,
        id_entidad: int | None = None,
        modelo: str | None = None,
        confianza: float | None = None,
        estado: str = "ok",
        latencia_ms: int = 0,
        codigo_error: str | None = None,
        salida: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Registra una decisión de IA. `hash_entrada` se calcula automáticamente
        a partir del payload de entrada.
        """
        raw = (
            payload_entrada
            if isinstance(payload_entrada, str)
            else repr(sorted((payload_entrada or {}).items()))
        )
        hash_entrada = sha256(raw.encode("utf-8")).hexdigest()

        row = DecisionesIARepository.insert(
            tipo=tipo,
            entidad=entidad,
            id_usuario_actor=id_usuario_actor,
            hash_entrada=hash_entrada,
            id_entidad=id_entidad,
            modelo=modelo,
            confianza=confianza,
            estado=estado,
            latencia_ms=latencia_ms,
            codigo_error=codigo_error,
        )
        if salida:
            DecisionesIAAtributosRepository.replace_for(
                row["id_decision"], "salida", salida
            )
        return cls.get_by_id(row["id_decision"])