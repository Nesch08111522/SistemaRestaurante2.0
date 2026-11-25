"""Personal favorites: explicit desired state, safe to submit again."""
from flask import jsonify, render_template
from app.core.auth_guard import login_required
from app.models.favorite import FavoriteModel
from app.models.restaurant import RestaurantModel
from app.blueprints.workspace import actor, body, WorkspaceError, workspace_errors
from . import bp


def published(restaurant):
    return bool(restaurant and restaurant.get('estado_publicacion') == 'published'
                and not restaurant.get('suspendido') and not restaurant.get('rechazado'))


@bp.get('/favorites')
@workspace_errors
@login_required
def favorites():
    favorites = FavoriteModel.list_by_usuario(actor()['id'])
    rows = []
    for item in favorites[:100]:
        restaurant = RestaurantModel.get_by_id(item['id_restaurante'], full=False)
        rows.append({'id':item['id_restaurante'], 'restaurant':restaurant if published(restaurant) else None})
    restaurants = [r for r in RestaurantModel.list_published(limit=100) if published(r)]
    return render_template('workspace/favorites.html', favorites=rows, restaurants=restaurants, truncated=len(favorites)>100)


@bp.put('/api/favorites/<int:restaurant_id>')
@workspace_errors
@login_required
def set_favorite(restaurant_id):
    data = body({'favorite'})
    if type(data.get('favorite')) is not bool:
        raise WorkspaceError('Indica si deseas guardar o quitar el favorito.')
    uid = actor()['id']
    if data['favorite']:
        if not published(RestaurantModel.get_by_id(restaurant_id, full=False)):
            raise WorkspaceError('El negocio no está disponible.', 404)
        FavoriteModel.add(uid, restaurant_id)
    else:
        # Removal is always scoped to the actor, even if the restaurant is no longer public.
        FavoriteModel.remove(uid, restaurant_id)
    return jsonify(success=True, favorite=data['favorite'])
