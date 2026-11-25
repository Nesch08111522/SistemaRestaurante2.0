# app/ai/prompts/recommend.py
"""Prompt para el recomendador de comensales."""

SYSTEM = """Eres un recomendador gastronómico de SmartResto.
Debes sugerir platos y restaurantes al usuario explicando el motivo.

REGLAS ESTRICTAS:
- Responde SOLO con un objeto JSON válido.
- NO inventes platos, restaurantes ni precios que no estén en el catálogo.
- Explica la razón de cada recomendación (máx 180 chars).
- Respeta restricciones alimentarias (vegano, vegetariano, celíaco, alergias).
- El campo `confianza` debe estar entre 0 y 1.

FORMATO DE RESPUESTA (JSON):
{
  "razon": "string (resumen general de la recomendación)",
  "items": [
    {"id": 1, "tipo": "plato|restaurante", "puntaje": 0.0, "razon": "string"}
  ],
  "confianza": 0.0
}
"""


def build_user_prompt(
    *,
    perfil: dict,
    restricciones: list[str],
    preferencias: list[str],
    catalogo: list[dict],
    contexto: str,
) -> str:
    return f"""Contexto: {contexto}

Perfil del usuario:
- Restricciones: {', '.join(restricciones) or 'ninguna'}
- Preferencias: {', '.join(preferencias) or 'ninguna'}

Catálogo disponible (máximo 30 platos):
{_format_catalogo(catalogo)}

Devuelve el JSON con las 3 mejores recomendaciones.
"""


def _format_catalogo(items: list[dict]) -> str:
    lines = []
    for it in items[:30]:
        lines.append(
            f"- id={it.get('id')} tipo={it.get('tipo')} "
            f"nombre={it.get('nombre')} restaurante={it.get('restaurante')} "
            f"precio={it.get('precio')} restricciones={it.get('restricciones')}"
        )
    return "\n".join(lines)