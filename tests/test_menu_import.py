from contextlib import nullcontext

import pytest

from app.services.errors import DomainError
from app.services import menu_import


def row(**changes):
    value = {
        "nombre": "Causa limeña", "precio": 18.5, "categoria": "Entradas",
        "descripcion": "Papa amarilla", "ingredientes": ["Papa", "Pollo"],
        "alergenos": ["Huevo"], "restricciones_dieteticas": ["Sin gluten"],
    }
    value.update(changes)
    return value


def test_confirmed_rows_revalidates_edited_preview():
    parsed = menu_import.confirmed_rows([row(nombre="  Causa  ")])
    assert parsed[0]["nombre"] == "Causa"
    assert parsed[0]["ingredientes"] == ["Papa", "Pollo"]
    with pytest.raises(DomainError, match="repetido"):
        menu_import.confirmed_rows([row(), row(nombre="causa limeña")])
    with pytest.raises(DomainError, match="lista"):
        menu_import.confirmed_rows([row(alergenos="huevo")])


def test_confirm_upserts_only_selected_restaurant(monkeypatch):
    calls = []
    from app.db import repository
    from app.repositories import menu3d, platos

    monkeypatch.setattr(repository, "shared_transaction", nullcontext)
    monkeypatch.setattr(platos.PlatosRepository, "list_by_restaurante", lambda rid: [
        {"id_plato": 4, "nombre": "Causa limeña"}
    ])
    monkeypatch.setattr(platos.PlatosRepository, "update_fields", lambda pid, data: calls.append(("update", pid, data)) or {"id_plato": pid})
    monkeypatch.setattr(platos.PlatosRepository, "insert", lambda **data: calls.append(("insert", data)) or {"id_plato": 9})
    monkeypatch.setattr(platos.PlatosIngredientesRepository, "replace_for", lambda pid, values: calls.append(("ingredients", pid, values)))
    monkeypatch.setattr(platos.PlatosRestriccionesDieteticasRepository, "replace_for", lambda pid, values: calls.append(("restrictions", pid, values)))
    monkeypatch.setattr(menu3d, "query", lambda sql, args: calls.append(("query", args)))

    result = menu_import.confirm(7, [row(), row(nombre="Ají de gallina")])

    assert result == {"created": 1, "updated": 1, "total": 2}
    assert ("update", 4, {"nombre": "Causa limeña", "precio": 18.5, "categoria": "Entradas", "descripcion": "Papa amarilla"}) in calls
    assert any(call[0] == "insert" and call[1]["id_restaurante"] == 7 for call in calls)
