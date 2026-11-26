# app/ai/recommender.py
"""Recomendador para comensales."""
from __future__ import annotations

from typing import Any

from app.ai.client import call_json
from app.ai.prompts.recommend import SYSTEM, build_user_prompt
from app.services.recommendations import rank_catalog


def recommend(
    *,
    id_usuario_actor: int,
    restricciones: list[str],
    preferencias: list[str],
    catalogo: list[dict],
    contexto: str = "busco algo rico cerca de mí",
    max_price: object | None = None,
    favorite_restaurant_ids: set[int] | None = None,
    search_terms: list[str] | None = None,
    origin: tuple[float, float] | None = None,
    feedback_by_dish: dict[int, str] | None = None,
) -> dict[str, Any]:
    """
    Genera recomendaciones con explicación.
    Respeta restricciones (el prompt lo exige) y no inventa catálogo.
    """
    shortlist = rank_catalog(
        catalog=catalogo, preferences=preferencias, restrictions=restricciones,
        max_price=max_price, favorite_restaurant_ids=favorite_restaurant_ids,
        search_terms=search_terms, origin=origin,
        feedback_by_dish=feedback_by_dish,
    )
    if not shortlist:
        return {"razon": "No hay opciones compatibles con las restricciones indicadas.", "items": [], "confianza": 1.0, "candidatos": []}
    response = call_json(
        kind="recommend",
        system_prompt=SYSTEM,
        user_prompt=build_user_prompt(
            perfil={},
            restricciones=restricciones,
            preferencias=preferencias,
            catalogo=shortlist,
            contexto=contexto,
        ),
        entidad="recomendacion",
        id_usuario_actor=id_usuario_actor,
        max_tokens=800,
        temperature=0.4,
        mock_payload={"total_catalogo": len(shortlist)},
    )
    allowed = {item["id"]: item for item in shortlist}
    items = []
    for item in response.get("items", []):
        if not isinstance(item, dict) or item.get("id") not in allowed:
            continue
        candidate = allowed[item["id"]]
        items.append({**item, "nombre": candidate.get("nombre"), "restaurante": candidate.get("restaurante"), "razones_deterministas": candidate["razones_deterministas"]})
    response["items"] = items or [{"id": item["id"], "tipo": item.get("tipo", "plato"), "puntaje": item["puntaje_determinista"] / 100, "razon": "; ".join(item["razones_deterministas"]), "nombre": item.get("nombre"), "restaurante": item.get("restaurante"), "razones_deterministas": item["razones_deterministas"]} for item in shortlist[:3]]
    response["candidatos"] = shortlist
    return response
