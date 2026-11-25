from unittest.mock import Mock
import pytest
from tests.test_qa_regression import app, data, sign_in
from app.models.review import ReviewModel
from app.models.search_history import SearchHistoryModel


def test_history_is_scoped_to_session_user(app, data, monkeypatch):
    get_history = Mock(return_value={'busquedas': [], 'envios': []})
    monkeypatch.setattr(SearchHistoryModel, 'get_full', get_history)
    with app.test_client() as client:
        sign_in(client)
        assert client.get('/auth/history').status_code == 200
    get_history.assert_called_once_with(1)


def test_reviews_reject_privileged_or_invalid_fields(app, data, monkeypatch):
    save = Mock(); monkeypatch.setattr('app.blueprints.auth.personal_routes.save_review', save)
    with app.test_client() as client:
        sign_in(client)
        for payload in ({'user_id': 2, 'restaurant_id': 1, 'rating': 5},
                        {'restaurant_id': 1, 'rating': 6},
                        {'restaurant_id': '1', 'rating': 5}):
            assert client.put('/auth/api/reviews', json=payload).status_code == 400
    save.assert_not_called()


def test_review_uses_only_active_user(app, data, monkeypatch):
    save = Mock(return_value={'id_resena': 8})
    monkeypatch.setattr('app.blueprints.auth.personal_routes.save_review', save)
    with app.test_client() as client:
        sign_in(client)
        response = client.put('/auth/api/reviews', json={'restaurant_id': 1, 'rating': 5, 'comment': 'Excelente'})
    assert response.status_code == 200
    save.assert_called_once_with(user_id=1, restaurant_id=1, rating=5, comment='Excelente')


def test_reviews_page_reads_only_active_user(app, data, monkeypatch):
    listing = Mock(return_value=[]); monkeypatch.setattr(ReviewModel, 'list_by_usuario', listing)
    with app.test_client() as client:
        sign_in(client)
        assert client.get('/auth/reviews').status_code == 200
    listing.assert_called_once_with(1, limit=100)
