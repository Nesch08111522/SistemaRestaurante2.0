# app/ai/vision.py
"""Análisis de fotos de platos con OpenRouter Vision."""
from __future__ import annotations

import base64
from typing import Any

from app.ai.client import call_json, is_mock
from app.ai.prompts.dish_from_photo import SYSTEM, build_user_prompt


def analyze_dish_photo(
    *,
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    notas: str | None = None,
    id_usuario_actor: int,
) -> dict[str, Any]:
    """
    Analiza una foto de plato y devuelve un borrador comercial.

    Si la IA no está configurada, devuelve un mock determinista.
    La foto NUNCA se persiste en disco: se envía como data URI en memoria.
    """
    if is_mock() or not image_bytes:
        return call_json(
            kind="dish_from_photo",
            system_prompt=SYSTEM,
            user_prompt=build_user_prompt(notas=notas),
            entidad="plato",
            id_usuario_actor=id_usuario_actor,
            mock_payload={"notas": notas, "tamano_bytes": len(image_bytes)},
        )

    encoded = base64.b64encode(image_bytes).decode("ascii")
    data_uri = f"data:{mime_type};base64,{encoded}"

    return call_json(
        kind="dish_from_photo",
        system_prompt=SYSTEM,
        user_prompt=build_user_prompt(notas=notas),
        entidad="plato",
        id_usuario_actor=id_usuario_actor,
        image_url=data_uri,
        max_tokens=800,
        temperature=0.2,
    )