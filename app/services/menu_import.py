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
