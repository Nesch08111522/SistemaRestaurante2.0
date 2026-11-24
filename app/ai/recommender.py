# app/ai/recommender.py
"""Recomendador para comensales."""
from __future__ import annotations

from typing import Any

from app.ai.client import call_json
from app.ai.prompts.recommend import SYSTEM, build_user_prompt


def recommend(
    *,
    id_usuario_actor: int,
    restricciones: list[str],
    preferencias: list[str],
    catalogo: list[dict],
    contexto: str = "busco algo rico cerca de mí",
) -> dict[str, Any]:
    """
    Genera recomendaciones con explicación.
    Respeta restricciones (el prompt lo exige) y no inventa catálogo.
    """
    return call_json(
        kind="recommend",
        system_prompt=SYSTEM,
        user_prompt=build_user_prompt(
            perfil={},
            restricciones=restricciones,
            preferencias=preferencias,
            catalogo=catalogo,
            contexto=contexto,
        ),
        entidad="recomendacion",
        id_usuario_actor=id_usuario_actor,
        max_tokens=800,
        temperature=0.4,
        mock_payload={"total_catalogo": len(catalogo)},
    )