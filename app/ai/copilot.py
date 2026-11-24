# app/ai/copilot.py
"""Copilot del empresario: audita menús, sugiere mejoras, redacta descripciones."""
from __future__ import annotations

from typing import Any

from app.ai.client import call_json
from app.ai.prompts.audit_menu import SYSTEM, build_user_prompt


def audit_menu(
    *,
    id_usuario_actor: int,
    platos: list[dict],
    id_restaurante: int | None = None,
) -> dict[str, Any]:
    """Audita un menú y devuelve problemas + sugerencias."""
    return call_json(
        kind="audit_menu",
        system_prompt=SYSTEM,
        user_prompt=build_user_prompt(platos=platos),
        entidad="restaurante",
        id_entidad=id_restaurante,
        id_usuario_actor=id_usuario_actor,
        max_tokens=1000,
        temperature=0.3,
        mock_payload={"total_platos": len(platos)},
    )