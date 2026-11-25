"""Private history and reviews, restricted to the active account."""
from flask import jsonify, render_template
from app.core.auth_guard import login_required
from app.models.review import ReviewModel
from app.models.restaurant import RestaurantModel
from app.models.search_history import SearchHistoryModel
from app.services.personal import save_review
from app.blueprints.workspace import actor, body, positive_id, text, workspace_errors
from . import bp


@bp.get('/history')
@workspace_errors
@login_required
def history():
    return render_template('workspace/history.html', history=SearchHistoryModel.get_full(actor()['id']))


@bp.get('/reviews')
@workspace_errors
@login_required
def reviews():
    own = ReviewModel.list_by_usuario(actor()['id'], limit=100)
    rows = []
    for review in own:
        restaurant = RestaurantModel.get_by_id(review['id_restaurante'], full=False)
        rows.append({**review, 'restaurant': restaurant})
    return render_template('workspace/reviews.html', reviews=rows,
                           restaurants=RestaurantModel.list_published(limit=100))


@bp.put('/api/reviews')
@workspace_errors
@login_required
def save_my_review():
    data = body({'restaurant_id', 'rating', 'comment'})
    restaurant_id = positive_id(data.get('restaurant_id'))
    rating = data.get('rating')
    if type(rating) is not int or not 1 <= rating <= 5:
        from app.blueprints.workspace import WorkspaceError
        raise WorkspaceError('La calificación debe estar entre 1 y 5.')
    comment = text(data.get('comment', ''), 'el comentario', 1000)
    review = save_review(user_id=actor()['id'], restaurant_id=restaurant_id,
                         rating=rating, comment=comment)
    return jsonify(success=True, review=review)
