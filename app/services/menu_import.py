"""Safe in-memory readers for restaurant menu CSV, XLSX and DOCX files."""
from __future__ import annotations

import csv
from datetime import date, datetime
from io import BytesIO, StringIO
from pathlib import PurePath
from typing import Any

from app.services.errors import DomainError

MAX_BYTES = 5 * 1024 * 1024
MAX_ROWS = 200
HEADERS = {"nombre", "precio", "categoria", "descripcion", "ingredientes", "alergenos", "restricciones_dieteticas"}


def _text(value: object, limit: int = 500) -> str:
    return " ".join(str(value or "").split())[:limit]


def _price(value: object) -> float:
    try:
        amount = float(str(value).replace("S/", "").replace(",", ".").strip())
    except (TypeError, ValueError):
        raise DomainError("Cada plato necesita un precio numérico válido.") from None
    if not 0 <= amount <= 999999:
        raise DomainError("El precio está fuera del rango permitido.")
    return round(amount, 2)


def _normalise_row(row: dict[str, object], row_number: int) -> dict[str, Any]:
    values = {str(key).strip().casefold(): _text(value) for key, value in row.items() if key}
    name = values.get("nombre", "")
    if not name:
        raise DomainError(f"Fila {row_number}: falta Nombre.")
    return {
        "fila": row_number, "nombre": name[:160], "precio": _price(values.get("precio")),
        "categoria": values.get("categoria", "")[:120], "descripcion": values.get("descripcion", "")[:1000],
        "ingredientes": [part.strip() for part in values.get("ingredientes", "").split(",") if part.strip()],
        "alergenos": [part.strip() for part in values.get("alergenos", "").split(",") if part.strip()],
        "restricciones_dieteticas": [part.strip() for part in values.get("restricciones_dieteticas", "").split(",") if part.strip()],
    }


def preview(filename: str, content: bytes) -> list[dict[str, Any]]:
    """Parse a menu upload without writing to disk or database."""
    if not filename or len(content) == 0:
        raise DomainError("El archivo está vacío.")
    if len(content) > MAX_BYTES:
        raise DomainError("El archivo supera el límite de 5 MB.", 413)
    suffix = PurePath(filename).suffix.casefold()
    if suffix == ".csv":
        try:
            rows = list(csv.DictReader(StringIO(content.decode("utf-8-sig"))))
        except UnicodeDecodeError:
            raise DomainError("El CSV debe estar codificado en UTF-8.") from None
    elif suffix == ".xlsx":
        try:
            from openpyxl import load_workbook
            workbook = load_workbook(BytesIO(content), read_only=True, data_only=True)
            sheet = workbook.active
            headers = [str(cell or "").strip() for cell in next(sheet.iter_rows(values_only=True))]
            rows = [dict(zip(headers, values)) for values in sheet.iter_rows(min_row=2, values_only=True)]
        except (ImportError, StopIteration, ValueError, KeyError) as exc:
            raise DomainError("El Excel no tiene una hoja de menú válida.") from exc
    elif suffix == ".docx":
        try:
            from docx import Document
            document = Document(BytesIO(content))
            rows = []
            for table in document.tables:
                header = [cell.text.strip() for cell in table.rows[0].cells]
                rows.extend(dict(zip(header, [cell.text for cell in table_row.cells])) for table_row in table.rows[1:])
        except (ImportError, IndexError, ValueError, KeyError) as exc:
            raise DomainError("El documento Word no contiene una tabla de menú válida.") from exc
    else:
        raise DomainError("Formato no soportado. Usa CSV, XLSX o DOCX.")
    if not rows or len(rows) > MAX_ROWS:
        raise DomainError(f"El archivo debe contener entre 1 y {MAX_ROWS} platos.")
    return [_normalise_row(row, index) for index, row in enumerate(rows, start=2)]


def _list(value: object, field: str) -> list[str]:
    """Validate a list that comes back from the client-side preview."""
    if value is None:
        return []
    if not isinstance(value, list):
        raise DomainError(f"{field} debe ser una lista.")
    result: list[str] = []
    seen = set()
    for item in value:
        if not isinstance(item, str):
            raise DomainError(f"{field} contiene un valor inválido.")
        clean = _text(item, 160)
        key = clean.casefold()
        if clean and key not in seen:
            seen.add(key)
            result.append(clean)
    return result


def confirmed_rows(rows: object) -> list[dict[str, Any]]:
    """Revalidate a browser-edited preview before it is allowed to persist."""
    if not isinstance(rows, list) or not rows or len(rows) > MAX_ROWS:
        raise DomainError(f"Debes confirmar entre 1 y {MAX_ROWS} platos.")
    result: list[dict[str, Any]] = []
    names = set()
    for position, raw in enumerate(rows, start=1):
        if not isinstance(raw, dict):
            raise DomainError(f"Plato {position}: formato inválido.")
        name = _text(raw.get("nombre"), 160)
        if not name:
            raise DomainError(f"Plato {position}: falta Nombre.")
        key = name.casefold()
        if key in names:
            raise DomainError(f"Plato {position}: el nombre está repetido en la importación.")
        names.add(key)
        result.append({
            "nombre": name,
            "precio": _price(raw.get("precio")),
            "categoria": _text(raw.get("categoria"), 120),
            "descripcion": _text(raw.get("descripcion"), 1000),
            "ingredientes": _list(raw.get("ingredientes"), "Ingredientes"),
            "alergenos": _list(raw.get("alergenos"), "Alérgenos"),
            "restricciones_dieteticas": _list(raw.get("restricciones_dieteticas"), "Restricciones dietéticas"),
        })
    return result


def confirm(restaurante_id: int, rows: object) -> dict[str, int]:
    """Atomically create or update a restaurant menu in PostgreSQL.

    A dish is updated only when a dish with the same normalized name already
    belongs to the selected restaurant.  This makes confirmation retry-safe
    without ever modifying another company's menu.
    """
    from app.db.repository import shared_transaction
    from app.repositories.menu3d import query
    from app.repositories.platos import (
        PlatosIngredientesRepository,
        PlatosRepository,
        PlatosRestriccionesDieteticasRepository,
    )

    clean_rows = confirmed_rows(rows)
    restaurant_id = int(restaurante_id)
    created = updated = 0
    with shared_transaction():
        existing = {
            _text(item.get("nombre"), 160).casefold(): item
            for item in PlatosRepository.list_by_restaurante(restaurant_id)
        }
        for row in clean_rows:
            payload = {
                "nombre": row["nombre"], "precio": row["precio"],
                "categoria": row["categoria"] or None,
                "descripcion": row["descripcion"] or None,
            }
            current = existing.get(row["nombre"].casefold())
            if current:
                dish = PlatosRepository.update_fields(current["id_plato"], payload)
                updated += 1
            else:
                dish = PlatosRepository.insert(id_restaurante=restaurant_id, **payload)
                created += 1
            dish_id = dish["id_plato"]
            PlatosIngredientesRepository.replace_for(dish_id, row["ingredientes"])
            PlatosRestriccionesDieteticasRepository.replace_for(
                dish_id, row["restricciones_dieteticas"]
            )
            # The existing catalog projection owns the allergen field.
            query(
                """INSERT INTO public.platos_menu3d(id_plato, alergenos)
                   VALUES (%s, %s)
                   ON CONFLICT(id_plato) DO UPDATE
                   SET alergenos=EXCLUDED.alergenos, actualizado_en=now()""",
                (dish_id, row["alergenos"]),
            )
            # Keep legacy readers ordered without deleting prior menu entries.
            query(
                """INSERT INTO public.restaurantes_platos(id_restaurante, posicion, id_plato)
                   SELECT %s, COALESCE(MAX(posicion), 0) + 1, %s
                   FROM public.restaurantes_platos WHERE id_restaurante=%s
                   HAVING NOT EXISTS (
                       SELECT 1 FROM public.restaurantes_platos
                       WHERE id_restaurante=%s AND id_plato=%s
                   )""",
                (restaurant_id, dish_id, restaurant_id, restaurant_id, dish_id),
            )
    return {"created": created, "updated": updated, "total": len(clean_rows)}
