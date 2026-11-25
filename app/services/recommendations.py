"""Deterministic, explainable restaurant recommendation before AI enrichment."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
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


def rank_catalog(*, catalog: list[dict[str, Any]], preferences: list[str], restrictions: list[str], max_price: object | None = None, limit: int = 12) -> list[dict[str, Any]]:
    """Return only compatible catalog entries with reproducible score and reasons.

    A dietary restriction is a hard exclusion unless the item explicitly declares
    the same restriction.  The language model can only explain this shortlist;
    it cannot reintroduce excluded or invented items.
    """
    preference_tokens = _tokens(preferences)
    restriction_tokens = _tokens(restrictions)
    budget = _number(max_price, Decimal("999999999")) if max_price is not None else None
    ranked: list[dict[str, Any]] = []
    for item in catalog:
        if not isinstance(item, dict) or not isinstance(item.get("id"), int):
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
        ranked.append({**item, "puntaje_determinista": float(min(score, Decimal("100"))), "razones_deterministas": reasons})
    ranked.sort(key=lambda row: (-row["puntaje_determinista"], str(row.get("nombre", "")).casefold(), row["id"]))
    return ranked[:max(1, min(limit, 30))]
