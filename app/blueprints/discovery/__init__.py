# app/blueprints/discovery/__init__.py
"""Blueprint de descubrimiento (radar, mapa, 3 caminos)."""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from app.models.restaurant import RestaurantModel

bp = Blueprint("discovery", __name__, template_folder="../../templates/discovery")


@bp.get("/")
def index():
    return render_template("discovery/index.html")


@bp.get("/api/restaurants")
def api_restaurants():
    q = (request.args.get("q") or "").strip()
    categoria = request.args.get("categoria")
    verificados = request.args.get("solo_verificados", "").lower() in ("1", "true", "yes", "on")

    candidatos = RestaurantModel.list_published(limit=200)

    if q:
        q_lower = q.lower()
        candidatos = [
            r for r in candidatos
            if q_lower in (r.get("nombre") or "").lower()
            or q_lower in (r.get("descripcion") or "").lower()
        ]
    if categoria:
        try:
            cid = int(categoria)
            candidatos = [r for r in candidatos if r.get("id_categoria") == cid]
        except ValueError:
            pass
    if verificados:
        candidatos = [r for r in candidatos if r.get("verificado") is True]

    distrito = (request.args.get("distrito") or "").strip().casefold()
    if distrito:
        candidatos = [r for r in candidatos if (r.get("distrito") or "").casefold() == distrito]
    precio = request.args.get("max_price")
    if precio:
        from decimal import Decimal, InvalidOperation
        try:
            maximum = Decimal(precio)
            if not maximum.is_finite() or maximum < 0:
                raise InvalidOperation
        except InvalidOperation:
            return jsonify({"error": "Precio máximo inválido"}), 400
        candidatos = [r for r in candidatos if r.get("precio_promedio") is not None and Decimal(str(r["precio_promedio"])) <= maximum]

    return jsonify({"total": len(candidatos), "restaurantes": candidatos}), 200


@bp.get("/api/map")
def api_map():
    candidatos = RestaurantModel.list_published(limit=500)
    puntos = [
        {
            "id": r.get("id_restaurante"),
            "nombre": r.get("nombre"),
            "lat": float(r["latitud"]) if r.get("latitud") is not None else None,
            "lng": float(r["longitud"]) if r.get("longitud") is not None else None,
            "categoria": r.get("id_categoria"),
            "calificacion": float(r["calificacion"]) if r.get("calificacion") is not None else None,
            "url": f"/negocio/{r.get('id_restaurante')}",
        }
        for r in candidatos
        if r.get("latitud") is not None and r.get("longitud") is not None
    ]
    return jsonify({"total": len(puntos), "puntos": puntos}), 200


# ---------- IA: recomendaciones ----------

@bp.post("/api/recommend")
def api_recommend():
    """
    Recomendación personalizada.
    Acepta JSON:
      {
        "restricciones": ["vegano", ...],
        "preferencias": ["mariscos", ...],
        "contexto": "quiero algo barato",
        "id_usuario": 0  (opcional, si no hay sesión se usa 0)
      }
    Devuelve las recomendaciones + explicación.
    """
    from flask import session
    from app.ai.recommender import recommend

    payload = request.get_json(silent=True) or {}
    restricciones = payload.get("restricciones") or []
    preferencias = payload.get("preferencias") or []
    contexto = payload.get("contexto") or "busco algo rico cerca de mí"

    user_id = session.get("user_id")
    id_usuario_actor = int(user_id) if user_id else 0

    # Catálogo simplificado de platos publicados
    restaurantes = RestaurantModel.list_published(limit=30)
    catalogo: list[dict] = []
    for r in restaurantes[:10]:
        menu = RestaurantModel.get_full_menu(r["id_restaurante"])
        for p in menu[:5]:
            catalogo.append({
                "id": p["id_plato"],
                "tipo": "plato",
                "nombre": p["nombre"],
                "restaurante": r["nombre"],
                "precio": float(p.get("precio") or 0),
                "restricciones": p.get("restricciones_dieteticas") or [],
            })

    resultado = recommend(
        id_usuario_actor=id_usuario_actor,
        restricciones=[str(x) for x in restricciones],
        preferencias=[str(x) for x in preferencias],
        catalogo=catalogo,
        contexto=str(contexto)[:300],
    )
    return jsonify({"success": True, "catalogo_total": len(catalogo), "recomendacion": resultado}), 200