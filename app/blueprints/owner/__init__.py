# app/blueprints/owner/__init__.py
"""Blueprint del panel del empresario."""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request, session

from app.core.auth_guard import empresa_required, login_required, role_required
from app.models.order import OrderModel
from app.models.restaurant import RestaurantModel
from app.models.review import ReviewModel

bp = Blueprint("owner", __name__, template_folder="../../templates/owner")


@bp.get("/")
@login_required
@empresa_required
@role_required("business_owner", "business_admin", "manager")
def dashboard():
    from flask import g
    empresa = g.empresa
    restaurantes = RestaurantModel.list_by_empresa(empresa["id_empresa"])
    total_resenas = 0
    promedio = 0.0
    for r in restaurantes:
        resumen = ReviewModel.summary(r["id_restaurante"])
        total_resenas += resumen["total_resenas"]
        promedio += resumen["promedio_calificacion"]
    if restaurantes:
        promedio = round(promedio / len(restaurantes), 2)
    return render_template(
        "owner/dashboard.html",
        empresa=empresa,
        restaurantes=restaurantes,
        total_resenas=total_resenas,
        promedio_calificacion=promedio,
    )


@bp.get("/api/resumen")
@login_required
@empresa_required
@role_required("business_owner", "business_admin", "manager")
def api_resumen():
    from flask import g
    empresa = g.empresa
    restaurantes = RestaurantModel.list_by_empresa(empresa["id_empresa"])
    return jsonify({
        "empresa": {
            "id": empresa["id_empresa"],
            "nombre": empresa["nombre"],
            "estado": empresa["estado"],
            "plan": (empresa.get("suscripcion") or {}).get("plan"),
        },
        "total_restaurantes": len(restaurantes),
        "restaurantes": [
            {"id": r["id_restaurante"], "nombre": r["nombre"], "estado": r.get("estado_publicacion")}
            for r in restaurantes
        ],
    }), 200


# ---------- IA: registrar plato por foto ----------

@bp.post("/api/ai/dish-from-photo")
@login_required
@empresa_required
@role_required("business_owner", "business_admin", "manager")
def api_ai_dish_from_photo():
    """
    Recibe multipart con `foto` y `notas` opcional.
    Devuelve un BORRADOR (no persiste el plato).
    """
    from app.ai.vision import analyze_dish_photo

    archivo = request.files.get("foto")
    if not archivo or not archivo.filename:
        return jsonify({"success": False, "error": "Falta el archivo `foto`."}), 400

    if not archivo.mimetype.startswith("image/"):
        return jsonify({"success": False, "error": "El archivo debe ser imagen."}), 400

    data = archivo.read()
    if not data:
        return jsonify({"success": False, "error": "Imagen vacía."}), 400
    if len(data) > 2 * 1024 * 1024:
        return jsonify({"success": False, "error": "Máximo 2 MB."}), 413

    notas = (request.form.get("notas") or "").strip() or None
    user_id = int(session["user_id"])

    resultado = analyze_dish_photo(
        image_bytes=data,
        mime_type=archivo.mimetype,
        notas=notas,
        id_usuario_actor=user_id,
    )
    return jsonify({
        "success": True,
        "borrador": resultado,
        "nota": "Borrador generado. El empresario debe confirmar ingredientes, alérgenos y precio antes de publicar.",
    }), 200


# ---------- IA: auditar menú ----------

@bp.post("/api/ai/audit-menu/<int:restaurante_id>")
@login_required
@empresa_required
@role_required("business_owner", "business_admin", "manager")
def api_ai_audit_menu(restaurante_id: int):
    from app.ai.copilot import audit_menu

    restaurante = RestaurantModel.get_by_id(restaurante_id, full=False)
    if not restaurante:
        return jsonify({"success": False, "error": "Restaurante no encontrado."}), 404

    from flask import abort, g
    if restaurante.get("id_empresa") != g.empresa["id_empresa"]:
        abort(403)
    menu = RestaurantModel.get_full_menu(restaurante_id)
    user_id = int(session["user_id"])

    resultado = audit_menu(
        id_usuario_actor=user_id,
        platos=menu,
        id_restaurante=restaurante_id,
    )
    return jsonify({"success": True, "auditoria": resultado}), 200