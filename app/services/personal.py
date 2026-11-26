"""Personal-history and review use cases, always scoped to the signed-in diner."""
from __future__ import annotations

from app.blueprints.workspace import WorkspaceError
from app.db.repository import shared_transaction
from app.models.restaurant import RestaurantModel
from app.repositories.resenas import ResenasRepository


def _published(restaurant: dict | None) -> bool:
    return bool(restaurant and restaurant.get("estado_publicacion") == "published"
                and not restaurant.get("suspendido") and not restaurant.get("rechazado"))


def save_review(*, user_id: int, restaurant_id: int, rating: int, comment: str) -> dict:
    if type(rating) is not int or not 1 <= rating <= 5:
        raise WorkspaceError("La calificación debe estar entre 1 y 5.")
    if not _published(RestaurantModel.get_by_id(restaurant_id, full=False)):
        raise WorkspaceError("El negocio no está disponible.", 404)

    # Serializes concurrent submissions for this diner/restaurant before querying.
    with shared_transaction() as conn, conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_xact_lock(%s, %s)", (int(user_id), int(restaurant_id)))
        cur.execute(
            "SELECT * FROM public.resenas WHERE id_usuario=%s AND id_restaurante=%s "
            "ORDER BY id_resena DESC LIMIT 1 FOR UPDATE",
            (int(user_id), int(restaurant_id)),
        )
        existing = cur.fetchone()
        if existing:
            cur.execute(
                "UPDATE public.resenas SET calificacion=%s, comentario=%s, "
                "actualizado_en=NOW() WHERE id_resena=%s RETURNING *",
                (rating, comment or None, existing["id_resena"]),
            )
        else:
            cur.execute(
                "INSERT INTO public.resenas (id_restaurante,id_usuario,calificacion,comentario,creado_en,actualizado_en) "
                "VALUES (%s,%s,%s,%s,NOW(),NOW()) RETURNING *",
                (int(restaurant_id), int(user_id), rating, comment or None),
            )
        review = cur.fetchone()
        # A review and its anchor are committed together; an unanchored review
        # is not silently accepted when traceability is enabled by migration.
        from app.services.traceability import enqueue_review
        enqueue_review(review)
        return review
