from app.services.recommendations import rank_catalog


def test_hybrid_rank_uses_favorites_history_promotions_and_distance():
    rows = rank_catalog(
        catalog=[
            {"id": 1, "id_restaurante": 4, "nombre": "Ceviche", "restaurante": "Mar Azul", "precio": 25,
             "restricciones": ["sin gluten"], "calificacion": 4.5, "promocion": True, "latitud": -12.04, "longitud": -77.03},
            {"id": 2, "id_restaurante": 5, "nombre": "Sopa", "restaurante": "Lejos", "precio": 25,
             "restricciones": ["sin gluten"], "calificacion": 4.5, "latitud": -13.04, "longitud": -78.03},
        ], preferences=[], restrictions=["sin gluten"], favorite_restaurant_ids={4},
        search_terms=["ceviche"], origin=(-12.04, -77.03),
    )
    assert rows[0]["id"] == 1
    assert rows[0]["distancia_km"] == 0.0
    assert any("favoritos" in reason for reason in rows[0]["razones_deterministas"])
    assert any("búsquedas anteriores" in reason for reason in rows[0]["razones_deterministas"])


def test_hybrid_rank_keeps_dietary_restrictions_hard():
    rows = rank_catalog(catalog=[{"id": 1, "nombre": "Normal", "precio": 10, "restricciones": []}],
                        preferences=[], restrictions=["vegano"])
    assert rows == []


def test_hybrid_rank_respects_private_feedback():
    catalog = [
        {"id": 1, "nombre": "Me gusta", "precio": 10, "restricciones": []},
        {"id": 2, "nombre": "Descartado", "precio": 10, "restricciones": []},
    ]
    rows = rank_catalog(catalog=catalog, preferences=[], restrictions=[],
                        feedback_by_dish={1: "me_interesa", 2: "no_me_interesa"})
    assert [row["id"] for row in rows] == [1]
    assert any("interés" in reason for reason in rows[0]["razones_deterministas"])
