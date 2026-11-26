"""Deterministic, explainable restaurant recommendation before AI enrichment."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from math import asin, cos, radians, sin, sqrt
from typing import Any
from unicodedata import normalize as unicode_normalize


def _token(value: object) -> str:
    text = unicode_normalize("NFKD", str(value or ""))
    return "".join(char for char in text.casefold() if not char.isascii() or char.isalnum() or char == " ").strip()


def _tokens(values: object) -> set[str]:
    if isinstance(values, str):
        values = values.split(",")
    return {_token(value) for value in values or [] if _token(value)} if isinstance(values, (list, tuple, set)) else set()


def _number(value: object, default: Decimal = Decimal("0")) -> Decimal:
    try:
        amount = Decimal(str(value))
        return amount if amount.is_finite() else default
    except (InvalidOperation, TypeError, ValueError):
        return default


def _distance_km(origin: tuple[float, float] | None, item: dict[str, Any]) -> float | None:
    if origin is None or item.get("latitud") is None or item.get("longitud") is None:
        return None
    try:
        lat1, lon1, lat2, lon2 = map(radians, (origin[0], origin[1], float(item["latitud"]), float(item["longitud"])))
    except (TypeError, ValueError):
        return None
    value = 2 * 6371.0088 * asin(sqrt(sin((lat2-lat1)/2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2-lon1)/2) ** 2))
    return round(value, 2)


def rank_catalog(*, catalog: list[dict[str, Any]], preferences: list[str], restrictions: list[str], max_price: object | None = None, limit: int = 12,
                 favorite_restaurant_ids: set[int] | None = None, search_terms: list[str] | None = None,
                 origin: tuple[float, float] | None = None,
                 feedback_by_dish: dict[int, str] | None = None) -> list[dict[str, Any]]:
    """Return only compatible catalog entries with reproducible score and reasons.

    A dietary restriction is a hard exclusion unless the item explicitly declares
    the same restriction.  The language model can only explain this shortlist;
    it cannot reintroduce excluded or invented items.
    """
    preference_tokens = _tokens(preferences)
    restriction_tokens = _tokens(restrictions)
    budget = _number(max_price, Decimal("999999999")) if max_price is not None else None
    favorites = favorite_restaurant_ids or set()
    searched = _tokens(search_terms or [])
    feedback = feedback_by_dish or {}
    ranked: list[dict[str, Any]] = []
    for item in catalog:
        if not isinstance(item, dict) or not isinstance(item.get("id"), int):
            continue
        if feedback.get(item["id"]) == "no_me_interesa":
            continue
        dietary = _tokens(item.get("restricciones"))
        tags = _tokens([item.get("nombre"), item.get("restaurante"), *(item.get("etiquetas") or [])]) | dietary
        if restriction_tokens and not restriction_tokens.issubset(dietary):
            continue
        price = _number(item.get("precio"))
        if budget is not None and price > budget:
            continue
        score = Decimal("20")
        reasons: list[str] = ["Disponible en el catálogo actual"]
        matches = preference_tokens & tags
        if matches:
            score += Decimal(min(45, 15 * len(matches)))
            reasons.append("Coincide con tus preferencias: " + ", ".join(sorted(matches)[:3]))
        if restriction_tokens:
            score += Decimal("25")
            reasons.append("Cumple tus restricciones alimentarias declaradas")
        rating = max(Decimal("0"), min(Decimal("5"), _number(item.get("calificacion"))))
        if rating:
            score += rating * Decimal("2")
            reasons.append(f"Valoración registrada: {rating:.1f}/5")
        if item.get("id_restaurante") in favorites:
            score += Decimal("8")
            reasons.append("Pertenece a un restaurante que guardaste en favoritos")
        if feedback.get(item["id"]) == "me_interesa":
            score += Decimal("10")
            reasons.append("Marcaste esta opción como de interés")
        searchable = _tokens([item.get("nombre"), item.get("restaurante"), item.get("categoria"), *(item.get("etiquetas") or [])])
        history_matches = searched & searchable
        if history_matches:
            score += Decimal(min(12, 4 * len(history_matches)))
            reasons.append("Coincide con tus búsquedas anteriores: " + ", ".join(sorted(history_matches)[:3]))
        if item.get("promocion"):
            score += Decimal("6")
            reasons.append("Tiene una promoción vigente registrada")
        distance = _distance_km(origin, item)
        if distance is not None:
            score += Decimal(str(max(0, 10 - min(distance, 10))))
            if distance <= 10:
                reasons.append(f"A {distance:.1f} km de tu ubicación")
        ranked.append({**item, "distancia_km": distance, "puntaje_determinista": float(min(score, Decimal("100"))), "razones_deterministas": reasons})
    ranked.sort(key=lambda row: (-row["puntaje_determinista"], str(row.get("nombre", "")).casefold(), row["id"]))
    return ranked[:max(1, min(limit, 30))]
