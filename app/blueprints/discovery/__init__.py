# app/blueprints/discovery/__init__.py
"""Blueprint de descubrimiento (radar, mapa, 3 caminos)."""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from app.core.auth_guard import login_required
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
    from app.models.search_history import SearchHistoryModel
    from app.repositories.favoritos import FavoritosRepository
    from app.repositories.promociones import PromocionesRepository
    from app.repositories.platos import PlatosRepository
    from app.repositories.feedback_recomendaciones_usuario import FeedbackRecomendacionesUsuarioRepository
    from app.repositories.usuarios import UsuariosPreferenciasRepository, UsuariosRestriccionesRepository

    payload = request.get_json(silent=True) or {}
    restricciones = payload.get("restricciones") or []
    preferencias = payload.get("preferencias") or []
    if (not isinstance(restricciones, list) or not isinstance(preferencias, list)
            or not all(isinstance(value, str) for value in [*restricciones, *preferencias])):
        return jsonify({"success": False, "error": "preferencias y restricciones deben ser listas de texto."}), 400
    contexto = payload.get("contexto") or "busco algo rico cerca de mí"

    user_id = session.get("user_id")
    id_usuario_actor = int(user_id) if user_id else 0
    if user_id:
        # Stored profile signals supplement, but never replace, explicit request values.
        preferencias = list(dict.fromkeys([*UsuariosPreferenciasRepository.list_for_user(id_usuario_actor), *preferencias]))
        restricciones = list(dict.fromkeys([*UsuariosRestriccionesRepository.list_for_user(id_usuario_actor), *restricciones]))
        history = SearchHistoryModel.get_full(id_usuario_actor)["busquedas"]
        search_terms = [entry.get("termino", "") for entry in history]
        favorites = {row["id_restaurante"] for row in FavoritosRepository.list_by_usuario(id_usuario_actor)}
        feedback = FeedbackRecomendacionesUsuarioRepository.list_for_user(id_usuario_actor)
    else:
        search_terms, favorites, feedback = [], set(), {}
    location = payload.get("ubicacion")
    origin = None
    if location is not None:
        if not isinstance(location, dict):
            return jsonify({"success": False, "error": "ubicacion debe incluir latitud y longitud."}), 400
        try:
            origin = (float(location["latitud"]), float(location["longitud"]))
            if not (-90 <= origin[0] <= 90 and -180 <= origin[1] <= 180):
                raise ValueError
        except (KeyError, TypeError, ValueError):
            return jsonify({"success": False, "error": "Ubicación inválida."}), 400
    max_price = payload.get("max_price")
    if max_price is not None:
        from decimal import Decimal, InvalidOperation
        try:
            parsed_price = Decimal(str(max_price))
            if not parsed_price.is_finite() or parsed_price < 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            return jsonify({"success": False, "error": "max_price es inválido."}), 400

    # Catálogo simplificado de platos publicados
    restaurantes = RestaurantModel.list_published(limit=30)
    catalogo: list[dict] = []
    for r in restaurantes[:10]:
        if r.get('suspendido') or r.get('rechazado'):
            continue
        menu = RestaurantModel.get_full_menu(r["id_restaurante"])
        public_ids = {row['id_plato'] for row in PlatosRepository.list_publicados(r['id_restaurante'])}
        promotion = bool(PromocionesRepository.list_by_restaurante(r["id_restaurante"], vigentes=True))
        for p in [dish for dish in menu if dish.get('id_plato') in public_ids][:5]:
            catalogo.append({
                "id": p["id_plato"],
                "tipo": "plato",
                "nombre": p["nombre"],
                "restaurante": r["nombre"],
                "id_restaurante": r["id_restaurante"],
                "precio": float(p.get("precio") or 0),
                "restricciones": p.get("restricciones_dieteticas") or [],
                "etiquetas": p.get("etiquetas") or [], "categoria": p.get("categoria"),
                "calificacion": r.get("calificacion"), "latitud": r.get("latitud"),
                "longitud": r.get("longitud"), "promocion": promotion,
            })

    resultado = recommend(
        id_usuario_actor=id_usuario_actor,
        restricciones=[str(x) for x in restricciones],
        preferencias=[str(x) for x in preferencias],
        catalogo=catalogo,
        contexto=str(contexto)[:300],
        max_price=max_price, favorite_restaurant_ids=favorites,
        search_terms=search_terms, origin=origin,
        feedback_by_dish=feedback,
    )
    if user_id and isinstance(contexto, str) and contexto.strip():
        SearchHistoryModel.register_search(id_usuario_actor, termino=contexto.strip()[:240], consulta=contexto.strip()[:240])
    return jsonify({"success": True, "catalogo_total": len(catalogo), "recomendacion": resultado}), 200


@bp.post("/api/recommend/feedback")
@login_required
def api_recommend_feedback():
    """Store a private positive or negative signal for a real catalog dish."""
    from flask import session
    from app.repositories.feedback_recomendaciones_usuario import FeedbackRecomendacionesUsuarioRepository
    from app.repositories.platos import PlatosRepository

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"success": False, "error": "Envía id_plato y valor."}), 400
    try:
        dish_id = int(payload.get("id_plato"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "id_plato es obligatorio."}), 400
    value = payload.get("valor")
    if value not in {"me_interesa", "no_me_interesa"}:
        return jsonify({"success": False, "error": "valor debe ser me_interesa o no_me_interesa."}), 400
    if not PlatosRepository.get_by_id(dish_id):
        return jsonify({"success": False, "error": "Plato no encontrado."}), 404
    row = FeedbackRecomendacionesUsuarioRepository.upsert(
        id_usuario=int(session["user_id"]), id_plato=dish_id, valor=value
    )
    return jsonify({"success": True, "feedback": row}), 200
