# app/ai/client.py
"""
Wrapper de OpenRouter con modo simulado (mock) y registro automático
en `decisiones_ia`.

- Si `OPENROUTER_API_KEY` está vacía, entra en modo mock y devuelve
  respuestas deterministas para que el proyecto se pueda probar sin
  gastar tokens.
- Cada llamada exitosa o fallida se registra en `decisiones_ia` con:
    tipo, entidad, id_entidad, id_usuario_actor, hash_entrada,
    modelo, confianza, latencia_ms, estado, codigo_error,
    y `salida` (atributos).
"""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)


_BASE_URL = os.getenv("AI_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
_MODEL = os.getenv("AI_MODEL", "openrouter/auto")
_VISION_MODEL = os.getenv("AI_VISION_MODEL", "openrouter/auto")
_TIMEOUT = int(os.getenv("AI_TIMEOUT", "45"))


def is_configured() -> bool:
    return bool(_API_KEY)


def is_mock() -> bool:
    return not is_configured()


# ============================================================
# MOCK: respuestas deterministas para pruebas sin API
# ============================================================

def _mock_response(kind: str, payload: dict) -> dict:
    if kind == "dish_from_photo":
        return {
            "nombre_sugerido": "Plato de prueba (mock)",
            "descripcion_sugerida": "Descripción generada en modo mock para pruebas.",
            "categoria_sugerida": "Plato Principal",
            "ingredientes_probables": ["ingrediente 1", "ingrediente 2"],
            "alergenos_probables": ["gluten"],
            "etiquetas_sugeridas": ["casero", "tradicional"],
            "confianza": 0.5,
        }
    if kind == "recommend":
        return {
            "razon": "Recomendación generada en modo mock.",
            "items": [
                {"id": 1, "tipo": "plato", "puntaje": 0.9, "razon": "Coincide con preferencias."},
                {"id": 2, "tipo": "plato", "puntaje": 0.8, "razon": "Buena relación calidad-precio."},
            ],
            "confianza": 0.5,
        }
    if kind == "audit_menu":
        return {
            "problemas": [
                {"ruta": "platos[0].descripcion", "severidad": "baja", "mensaje": "Descripción muy corta."},
            ],
            "sugerencias": [
                "Ampliar descripción del plato 0.",
                "Agregar alérgenos declarados.",
            ],
            "confianza": 0.5,
        }
    return {"mock": True, "kind": kind, "echo": payload, "confianza": 0.0}


# ============================================================
# LLAMADA REAL A OPENROUTER
# ============================================================

def _call_openrouter(
    *,
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.3,
    image_url: str | None = None,
) -> dict[str, Any]:
    """
    Llama a OpenRouter y devuelve:
      {"content": str, "modelo": str, "tokens": {"prompt": int, "completion": int, "total": int}}
    """
    headers = {
        "Authorization": f"Bearer {_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("AI_REFERER", "http://localhost:5000"),
        "X-Title": "SmartResto",
    }

    messages: list[dict] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": [{"type": "text", "text": user_prompt}]},
    ]
    if image_url:
        messages[1]["content"].append({
            "type": "image_url",
            "image_url": {"url": image_url},
        })

    body = {
        "model": model or _MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    started = time.perf_counter()
    resp = requests.post(
        f"{_BASE_URL}/chat/completions",
        headers=headers,
        data=json.dumps(body),
        timeout=_TIMEOUT,
    )
    elapsed_ms = int((time.perf_counter() - started) * 1000)

    if resp.status_code == 429:
        raise _AIRateLimited("OpenRouter devolvió 429 (rate limit).")
    if resp.status_code >= 500:
        raise _AIUnavailable(f"OpenRouter devolvió {resp.status_code}.")
    if not resp.ok:
        raise _AIError(f"OpenRouter error {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    choices = data.get("choices") or []
    if not choices:
        raise _AIError("OpenRouter no devolvió choices.")

    content = choices[0].get("message", {}).get("content") or ""
    usage = data.get("usage") or {}
    return {
        "content": content,
        "modelo": data.get("model", model or _MODEL),
        "tokens": {
            "prompt": int(usage.get("prompt_tokens", 0)),
            "completion": int(usage.get("completion_tokens", 0)),
            "total": int(usage.get("total_tokens", 0)),
        },
        "elapsed_ms": elapsed_ms,
    }


class _AIError(Exception):
    """Error genérico de IA."""


class _AIRateLimited(_AIError):
    """Rate limit."""


class _AIUnavailable(_AIError):
    """Servicio no disponible."""


# ============================================================
# FACHADA PRINCIPAL: llama + registra en decisiones_ia
# ============================================================

def call_json(
    *,
    kind: str,
    system_prompt: str,
    user_prompt: str,
    entidad: str,
    id_usuario_actor: int,
    id_entidad: int | None = None,
    modelo: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.3,
    image_url: str | None = None,
    mock_payload: dict | None = None,
) -> dict[str, Any]:
    """
    Llama a la IA, parsea JSON de la respuesta y registra en `decisiones_ia`.

    Si la IA está en modo mock o falla, usa `_mock_response(kind, mock_payload)`
    para no romper el flujo de la app.
    """
    from app.models.ai_decision import AIDecisionModel

    payload_entrada = {
        "kind": kind,
        "system": system_prompt[:200],
        "user": user_prompt[:500],
        "imagen": bool(image_url),
    }

    started = time.perf_counter()

    # ---------- Modo mock ----------
    if is_mock():
        mock = _mock_response(kind, mock_payload or {})
        latencia = int((time.perf_counter() - started) * 1000)
        _registrar_decision(
            tipo=kind,
            entidad=entidad,
            id_entidad=id_entidad,
            id_usuario_actor=id_usuario_actor,
            payload_entrada=payload_entrada,
            modelo="mock",
            confianza=mock.get("confianza", 0.0),
            latencia_ms=latencia,
            estado="cache",
            salida=[
                {"ruta": "mock", "tipo_valor": "booleano", "valor_booleano": True},
                {"ruta": "kind", "tipo_valor": "texto", "valor_texto": kind},
            ],
        )
        return mock

    # ---------- Llamada real ----------
    try:
        result = _call_openrouter(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=modelo,
            max_tokens=max_tokens,
            temperature=temperature,
            image_url=image_url,
        )
    except _AIRateLimited:
        _registrar_decision(
            tipo=kind, entidad=entidad, id_entidad=id_entidad,
            id_usuario_actor=id_usuario_actor, payload_entrada=payload_entrada,
            modelo=modelo or _MODEL, confianza=None,
            latencia_ms=int((time.perf_counter() - started) * 1000),
            estado="rate_limited", codigo_error="HTTP_429",
        )
        return _mock_response(kind, {**mock_payload, "degradado": "rate_limited"})
    except _AIUnavailable:
        _registrar_decision(
            tipo=kind, entidad=entidad, id_entidad=id_entidad,
            id_usuario_actor=id_usuario_actor, payload_entrada=payload_entrada,
            modelo=modelo or _MODEL, confianza=None,
            latencia_ms=int((time.perf_counter() - started) * 1000),
            estado="unavailable", codigo_error="HTTP_5XX",
        )
        return _mock_response(kind, {**mock_payload, "degradado": "unavailable"})
    except _AIError as error:
        _registrar_decision(
            tipo=kind, entidad=entidad, id_entidad=id_entidad,
            id_usuario_actor=id_usuario_actor, payload_entrada=payload_entrada,
            modelo=modelo or _MODEL, confianza=None,
            latencia_ms=int((time.perf_counter() - started) * 1000),
            estado="error", codigo_error=str(error)[:48],
        )
        logger.warning("Fallo IA (%s): %s", kind, error)
        return _mock_response(kind, {**mock_payload, "degradado": "error"})
    except Exception as error:  # noqa: BLE001
        _registrar_decision(
            tipo=kind, entidad=entidad, id_entidad=id_entidad,
            id_usuario_actor=id_usuario_actor, payload_entrada=payload_entrada,
            modelo=modelo or _MODEL, confianza=None,
            latencia_ms=int((time.perf_counter() - started) * 1000),
            estado="error", codigo_error=type(error).__name__[:48],
        )
        logger.exception("Error inesperado en IA (%s)", kind)
        return _mock_response(kind, {**mock_payload, "degradado": "exception"})

    # ---------- Parsear JSON ----------
    parsed = _safe_json(result["content"])
    if parsed is None:
        _registrar_decision(
            tipo=kind, entidad=entidad, id_entidad=id_entidad,
            id_usuario_actor=id_usuario_actor, payload_entrada=payload_entrada,
            modelo=result["modelo"], confianza=None,
            latencia_ms=result["elapsed_ms"],
            estado="error", codigo_error="invalid_json",
        )
        logger.warning("Respuesta IA no es JSON: %s", result["content"][:200])
        return _mock_response(kind, {**mock_payload, "degradado": "invalid_json"})

    # ---------- Registrar éxito ----------
    salida_attrs = _json_to_attrs(parsed)
    _registrar_decision(
        tipo=kind, entidad=entidad, id_entidad=id_entidad,
        id_usuario_actor=id_usuario_actor, payload_entrada=payload_entrada,
        modelo=result["modelo"], confianza=parsed.get("confianza"),
        latencia_ms=result["elapsed_ms"], estado="ok",
        salida=salida_attrs,
    )
    parsed["_meta"] = {
        "modelo": result["modelo"],
        "tokens": result["tokens"],
        "latencia_ms": result["elapsed_ms"],
    }
    return parsed


# ============================================================
# Helpers
# ============================================================

def _registrar_decision(
    *,
    tipo: str,
    entidad: str,
    id_entidad: int | None,
    id_usuario_actor: int,
    payload_entrada: dict,
    modelo: str,
    confianza: float | None,
    latencia_ms: int,
    estado: str,
    codigo_error: str | None = None,
    salida: list[dict] | None = None,
) -> None:
    """Registra la decisión en `decisiones_ia`. Falla silenciosa para no romper."""
    try:
        from app.models.ai_decision import AIDecisionModel
        AIDecisionModel.record(
            tipo=tipo,
            entidad=entidad,
            id_usuario_actor=id_usuario_actor,
            payload_entrada=payload_entrada,
            id_entidad=id_entidad,
            modelo=modelo,
            confianza=confianza,
            estado=estado,
            latencia_ms=latencia_ms,
            codigo_error=codigo_error,
            salida=salida,
        )
    except Exception:
        logger.exception("No se pudo registrar la decisión IA en BD.")


def _safe_json(text: str) -> dict | None:
    """
    Extrae el primer objeto JSON de `text`.
    Tolera respuestas con texto adicional antes o después del JSON.
    """
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        # quitar bloque markdown
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def _json_to_attrs(obj: Any, prefix: str = "", out: list | None = None) -> list[dict]:
    """Aplana un dict/list en atributos con `ruta` y `tipo_valor`."""
    if out is None:
        out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            _json_to_attrs(v, f"{prefix}.{k}" if prefix else str(k), out)
    elif isinstance(obj, list):
        for idx, v in enumerate(obj):
            _json_to_attrs(v, f"{prefix}[{idx}]", out)
    elif isinstance(obj, bool):
        out.append({"ruta": prefix, "tipo_valor": "booleano", "valor_booleano": obj})
    elif isinstance(obj, (int, float)):
        out.append({"ruta": prefix, "tipo_valor": "numero", "valor_numero": obj})
    elif obj is None:
        out.append({"ruta": prefix, "tipo_valor": "nulo"})
    else:
        out.append({"ruta": prefix, "tipo_valor": "texto", "valor_texto": str(obj)[:2000]})
    return out