
from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    render_template,
    request,
    send_from_directory,
)

from app.models.user import UserModel
from app.core.security import fresh_session_user

bp = Blueprint("public", __name__)


# ============================================================
# SEGURIDAD: PROTECCIÓN DE RECURSOS PRIVADOS
# ============================================================

@bp.before_request
def protect_private_resources():
    """
    Protege los endpoints privados de la API pública.

    Reglas:
    - ADMIN: acceso global.
    - Usuarios normales: acceso únicamente a sus propios recursos.
    - Empresas y restaurantes: validación de permisos.
    - Recursos administrativos: exclusivos de ADMIN.
    """

    endpoint = (request.endpoint or "").removeprefix("public.")
    args = request.view_args or {}

    admin_only = {
        "api_ai_decision",
        "api_moderation",
        "api_discovery_sources",
        "api_discovery_due",
        "api_audit",
        "api_group",
    }

    needs_auth = (
        "user_id" in args
        or endpoint in admin_only
        or endpoint in {
            "api_company",
            "api_restaurant_orders",
            "api_order",
        }
    )

    if not needs_auth:
        return None

    user = fresh_session_user()

    if not user:
        return jsonify({"error": "unauthorized"}), 401

    if user.get("role") == "admin":
        return None

    if endpoint in admin_only:
        abort(403)

    # --------------------------------------------------------
    # Recursos asociados directamente a un usuario
    # --------------------------------------------------------

    if "user_id" in args:
        if user.get("id") != args["user_id"]:
            abort(403)

        return None

    # --------------------------------------------------------
    # Permisos de empresas
    # --------------------------------------------------------

    from app.models.company import permitted

    if endpoint == "api_company":
        if not permitted(
            user,
            args["empresa_id"],
            "business.manage",
        ):
            abort(403)

        return None

    # --------------------------------------------------------
    # Permisos de restaurantes y pedidos
    # --------------------------------------------------------

    from app.models.restaurant import RestaurantModel

    restaurant_id = args.get("restaurante_id")

    if endpoint == "api_order":
        from app.models.order import OrderModel

        order = OrderModel.get_by_id(
            args["pedido_id"],
            full=False,
        )

        if not order:
            abort(404)

        # El propietario del pedido puede consultarlo.
        if order.get("id_usuario") == user.get("id"):
            return None

        restaurant_id = order.get("id_restaurante")

    restaurant = (
        RestaurantModel.get_by_id(
            restaurant_id,
            full=False,
        )
        if restaurant_id
        else None
    )

    if not restaurant:
        abort(403)

    if not permitted(
        user,
        restaurant["id_empresa"],
        "orders.read.business",
    ):
        abort(403)

    return None


# ============================================================
# PÁGINA PRINCIPAL
# ============================================================

@bp.get("/")
def home():
    """
    Página principal editorial Forest.

    Obtiene:
    - Categorías desde la base de datos.
    - Restaurantes publicados.
    - Máximo 6 restaurantes para la página principal.
    """

    from app.repositories.categorias import CategoriasRepository
    from app.repositories.restaurantes import RestaurantesRepository

    try:
        categories = CategoriasRepository.list_all()
    except Exception:
        current_app.logger.exception(
            "Error al obtener categorías para la página principal."
        )
        categories = []

    try:
        restaurants = RestaurantesRepository.list_published(
            limit=6
        )
    except Exception:
        current_app.logger.exception(
            "Error al obtener restaurantes publicados."
        )
        restaurants = []

    return render_template(
        "public/home.html",
        categories=categories,
        restaurants=restaurants,
    )


# ============================================================
# PWA: PÁGINA OFFLINE
# ============================================================


@bp.get("/para-negocios")
def business_plans():
    """Public business plans and product preview."""
    return render_template("business_plans.html")


@bp.get("/offline")
def offline():
    """
    Página de respaldo cuando el usuario pierde la conexión.

    Archivo esperado:
        templates/offline.html
    """

    return render_template("offline.html")


# ============================================================
# PWA: SERVICE WORKER
# ============================================================

@bp.get("/sw.js")
def service_worker():
    """
    Sirve el Service Worker desde la raíz del dominio.

    Es importante que esté disponible en /sw.js
    para que pueda controlar toda la aplicación.

    Archivo esperado:
        static/sw.js
    """

    response = send_from_directory(
        current_app.static_folder,
        "sw.js",
    )

    response.headers["Content-Type"] = "application/javascript"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# ============================================================
# FASE 1: AUTENTICACIÓN Y USUARIOS
# ============================================================

@bp.get("/api/me")
def api_me():
    user = fresh_session_user()

    if not user:
        return jsonify({
            "authenticated": False,
            "user": None,
        }), 200

    return jsonify({
        "authenticated": True,
        "user": user,
    }), 200


@bp.get("/api/user/<int:user_id>")
def api_user(user_id: int):
    row = UserModel.get_by_id(user_id)

    if not row:
        return jsonify({"error": "not_found"}), 404

    row = {
        key: value
        for key, value in row.items()
        if key != "password"
    }

    return jsonify(row), 200


# ============================================================
# FASE 2: EMPRESAS
# ============================================================

@bp.get("/api/company/<int:empresa_id>")
def api_company(empresa_id: int):
    from app.repositories.empresas import EmpresasRepository

    empresa = EmpresasRepository.get_by_id(empresa_id)

    if not empresa:
        return jsonify({"error": "not_found"}), 404

    return jsonify(empresa), 200


@bp.get("/api/user/<int:user_id>/companies")
def api_user_companies(user_id: int):
    from app.models.company import get_company_for_user

    return jsonify(
        get_company_for_user(user_id) or {}
    ), 200


# ============================================================
# FASE 3: CATÁLOGO Y RESTAURANTES
# ============================================================

@bp.get("/api/restaurant/<int:restaurante_id>")
def api_restaurant(restaurante_id: int):
    from app.models.restaurant import RestaurantModel

    row = RestaurantModel.get_by_id(
        restaurante_id,
        full=True,
    )

    if not row:
        return jsonify({"error": "not_found"}), 404

    return jsonify(row), 200


@bp.get("/api/restaurant/<int:restaurante_id>/menu")
def api_restaurant_menu(restaurante_id: int):
    from app.models.restaurant import RestaurantModel

    menu = RestaurantModel.get_full_menu(restaurante_id)

    return jsonify({
        "restaurante_id": restaurante_id,
        "platos": menu,
    }), 200


@bp.get("/api/categorias")
def api_categorias():
    from app.repositories.categorias import CategoriasRepository

    return jsonify(
        CategoriasRepository.list_all()
    ), 200


@bp.get("/api/restaurants/published")
def api_restaurants_published():
    from app.models.restaurant import RestaurantModel

    return jsonify(
        RestaurantModel.list_published(limit=20)
    ), 200


# ============================================================
# FASE 4: OPERACIONES
# ============================================================

@bp.get("/api/restaurant/<int:restaurante_id>/menus")
def api_menus(restaurante_id: int):
    from app.models.menu import MenuModel

    return jsonify(
        MenuModel.list_by_restaurante(
            restaurante_id,
            full=True,
        )
    ), 200


@bp.get("/api/restaurant/<int:restaurante_id>/reviews")
def api_reviews(restaurante_id: int):
    from app.models.review import ReviewModel

    return jsonify({
        "resenas": ReviewModel.list_by_restaurante(
            restaurante_id,
            limit=20,
        ),
        "resumen": ReviewModel.summary(restaurante_id),
    }), 200


@bp.get("/api/restaurant/<int:restaurante_id>/promotions")
def api_promotions(restaurante_id: int):
    from app.models.promotion import PromotionModel

    return jsonify(
        PromotionModel.list_by_restaurante(
            restaurante_id,
            vigentes=True,
        )
    ), 200


@bp.get("/api/user/<int:user_id>/favorites")
def api_favorites(user_id: int):
    from app.models.favorite import FavoriteModel

    return jsonify(
        FavoriteModel.list_by_usuario(user_id)
    ), 200


@bp.get("/api/user/<int:user_id>/notifications")
def api_notifications(user_id: int):
    from app.models.notification import NotificationModel

    return jsonify({
        "notificaciones": NotificationModel.list_by_usuario(
            user_id,
            limit=20,
        ),
        "no_leidas": NotificationModel.count_unread(user_id),
    }), 200


# ============================================================
# FASE 5: PEDIDOS
# ============================================================

@bp.get("/api/user/<int:user_id>/orders")
def api_user_orders(user_id: int):
    from app.models.order import OrderModel

    return jsonify(
        OrderModel.list_by_usuario(
            user_id,
            limit=20,
        )
    ), 200


@bp.get("/api/restaurant/<int:restaurante_id>/orders")
def api_restaurant_orders(restaurante_id: int):
    from app.models.order import OrderModel

    return jsonify(
        OrderModel.list_by_restaurante(
            restaurante_id,
            limit=20,
        )
    ), 200


@bp.get("/api/order/<int:pedido_id>")
def api_order(pedido_id: int):
    from app.models.order import OrderModel

    row = OrderModel.get_by_id(
        pedido_id,
        full=True,
    )

    if not row:
        return jsonify({"error": "not_found"}), 404

    return jsonify(row), 200


# ============================================================
# FASE 6: IA, MODERACIÓN Y FEEDBACK
# ============================================================

@bp.get("/api/ai-decisions/<int:id_decision>")
def api_ai_decision(id_decision: int):
    from app.models.ai_decision import AIDecisionModel

    row = AIDecisionModel.get_by_id(id_decision)

    if not row:
        return jsonify({"error": "not_found"}), 404

    return jsonify(row), 200


@bp.get("/api/moderations/<int:id_moderacion>")
def api_moderation(id_moderacion: int):
    from app.models.moderation import ModerationModel

    row = ModerationModel.get_by_id(
        id_moderacion,
        full=True,
    )

    if not row:
        return jsonify({"error": "not_found"}), 404

    return jsonify(row), 200


@bp.get("/api/user/<int:user_id>/search-history")
def api_search_history(user_id: int):
    from app.models.search_history import SearchHistoryModel

    return jsonify(
        SearchHistoryModel.get_full(user_id)
    ), 200


# ============================================================
# FASE 7: DESCUBRIMIENTO, AUDITORÍA Y GRUPOS
# ============================================================

@bp.get("/api/discovery/sources")
def api_discovery_sources():
    from app.models.discovery import DiscoveryModel

    return jsonify(
        DiscoveryModel.list_sources()
    ), 200


@bp.get("/api/discovery/due")
def api_discovery_due():
    from app.models.discovery import DiscoveryModel

    return jsonify(
        DiscoveryModel.list_due(limit=10)
    ), 200


@bp.get("/api/audit/<int:id_evento>")
def api_audit(id_evento: int):
    from app.models.audit import AuditModel

    row = AuditModel.get_full(id_evento)

    if not row:
        return jsonify({"error": "not_found"}), 404

    return jsonify(row), 200


@bp.get("/api/groups/<int:id_grupo>")
def api_group(id_grupo: int):
    from app.models.food_group import FoodGroupModel

    row = FoodGroupModel.get_by_id(
        id_grupo,
        full=True,
    )

    if not row:
        return jsonify({"error": "not_found"}), 404

    return jsonify(row), 200


# ============================================================
# FASE 8: COCINAS DE MERCADO
# ============================================================

@bp.get("/api/market-kitchens")
def api_market_kitchens():
    from app.models.market_kitchen import MarketKitchenModel

    return jsonify(
        MarketKitchenModel.list_all()
    ), 200


@bp.get("/api/market-kitchen/<int:id_cocina>")
def api_market_kitchen(id_cocina: int):
    from app.models.market_kitchen import MarketKitchenModel

    row = MarketKitchenModel.get_by_id(
        id_cocina,
        full=True,
    )

    if not row:
        return jsonify({"error": "not_found"}), 404

    return jsonify(row), 200
