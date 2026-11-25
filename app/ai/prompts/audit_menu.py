# app/ai/prompts/audit_menu.py
"""Prompt para auditar un menú completo."""

SYSTEM = """Eres un auditor de menús de SmartResto.
Analizas un menú y detectas problemas de presentación, precios, ingredientes, alérgenos y consistencia.

REGLAS ESTRICTAS:
- Responde SOLO con un objeto JSON válido.
- Severidad ∈ {baja, media, alta}.
- No inventes platos ni datos.
- `confianza` entre 0 y 1.

FORMATO DE RESPUESTA (JSON):
{
  "problemas": [
    {"ruta": "platos[0].descripcion", "severidad": "baja|media|alta", "mensaje": "string"}
  ],
  "sugerencias": ["string", ...],
  "confianza": 0.0
}
"""


def build_user_prompt(*, platos: list[dict]) -> str:
    return f"""Audita el siguiente menú (máximo 50 platos):

{_format_platos(platos)}

Devuelve el JSON con problemas y sugerencias.
"""


def _format_platos(platos: list[dict]) -> str:
    lines = []
    for idx, p in enumerate(platos[:50]):
        lines.append(
            f"[{idx}] nombre={p.get('nombre')} precio={p.get('precio')} "
            f"descripcion={(p.get('descripcion') or '')[:80]} "
            f"categoria={p.get('categoria')} "
            f"ingredientes={p.get('ingredientes')}"
        )
    return "\n".join(lines)