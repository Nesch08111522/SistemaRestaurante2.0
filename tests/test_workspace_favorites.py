from unittest.mock import Mock
import pytest
from tests.test_qa_regression import app, data, sign_in
from app.models.favorite import FavoriteModel
from app.models.restaurant import RestaurantModel

def test_favorite_retries_preserve_desired_state_and_actor(app,data,monkeypatch):
    add=Mock();monkeypatch.setattr(FavoriteModel,'add',add)
    with app.test_client() as c:
        sign_in(c)
        for _ in range(2): assert c.put('/auth/api/favorites/1',json={'favorite':True}).status_code==200
        assert c.put('/auth/api/favorites/1',json={'favorite':True,'id_usuario':2}).status_code==400
    assert add.call_count==2
    add.assert_called_with(1,1)

def test_cannot_favorite_unpublished_restaurant(app,data,monkeypatch):
    monkeypatch.setattr(RestaurantModel,'get_by_id',lambda *a,**k: {'estado_publicacion':'draft'})
    add=Mock();monkeypatch.setattr(FavoriteModel,'add',add)
    with app.test_client() as c:
        sign_in(c)
        assert c.put('/auth/api/favorites/1',json={'favorite':True}).status_code==404
    add.assert_not_called()

def test_remove_scopes_to_actor_even_when_not_published(app,data,monkeypatch):
    remove=Mock();monkeypatch.setattr(FavoriteModel,'remove',remove)
    with app.test_client() as c:
        sign_in(c)
        assert c.put('/auth/api/favorites/5',json={'favorite':False}).status_code==200
    remove.assert_called_once_with(1,5)

def test_favorites_page_escapes_content(app,data,monkeypatch):
    monkeypatch.setattr(FavoriteModel,'list_by_usuario',lambda *a:[{'id_restaurante':1}])
    monkeypatch.setattr(RestaurantModel,'get_by_id',lambda *a,**k: {'estado_publicacion':'published','nombre':'<script>alert(1)</script>'})
    with app.test_client() as c:
        sign_in(c);response=c.get('/auth/favorites')
        assert response.status_code==200
        assert '<script>alert(1)</script>' not in response.text
        assert '&lt;script&gt;' in response.text
