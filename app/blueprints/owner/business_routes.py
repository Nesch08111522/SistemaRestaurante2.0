"""Self-service business registration; writes remain atomic and tenant scoped."""
from uuid import uuid4
from flask import flash, g, redirect, request, url_for
from app.core.auth_guard import empresa_required, login_required, role_required
from app.blueprints.workspace import actor, text, workspace_errors, WorkspaceError
from app.db.repository import shared_transaction
from app.models.company import create_company_with_owner, get_company_for_user, permitted
from app.repositories.restaurantes import RestaurantesRepository
from . import bp


def restaurant_fields():
    values = {name: text(request.form.get(name), name, maximum, required=True)
            for name, maximum in [('restaurante',120),('direccion',250),('distrito',100)]}
    if len(values['restaurante']) < 2:
        raise WorkspaceError('El nombre del restaurante debe tener al menos 2 caracteres.')
    return values


@bp.post('/registrar')
@workspace_errors
@login_required
@role_required('business_owner')
def create_business():
    user = actor()
    name = text(request.form.get('empresa'), 'empresa', 120, required=True)
    if len(name) < 2:
        raise WorkspaceError('El nombre de la empresa debe tener al menos 2 caracteres.')
    values = restaurant_fields()
    with shared_transaction() as conn, conn.cursor() as cur:
        # Lock the account so double submissions cannot create two businesses.
        cur.execute('SELECT id_usuario FROM public.usuarios WHERE id_usuario=%s FOR UPDATE', (user['id'],))
        if get_company_for_user(user['id']):
            return redirect(url_for('owner.dashboard'), code=303)
        company = create_company_with_owner(owner_user_id=user['id'],
            identificador_url='negocio-' + uuid4().hex, nombre=name, plan='basic')
        RestaurantesRepository.insert(id_empresa=company['id_empresa'], id_propietario=user['id'],
            id_categoria=None, nombre=values['restaurante'], direccion=values['direccion'], distrito=values['distrito'])
    flash('Empresa y restaurante registrados. Ya puedes abrir tu panel.', 'success')
    return redirect(url_for('owner.dashboard'), code=303)


@bp.post('/restaurantes')
@workspace_errors
@login_required
@role_required('business_owner','business_admin','manager')
@empresa_required
def create_restaurant():
    user = actor()
    if not permitted(user, g.empresa['id_empresa'], 'branch.manage'):
        raise WorkspaceError('Tu membresía no permite registrar restaurantes.', 403)
    values = restaurant_fields()
    RestaurantesRepository.insert(id_empresa=g.empresa['id_empresa'], id_propietario=user['id'],
        id_categoria=None, nombre=values['restaurante'], direccion=values['direccion'], distrito=values['distrito'])
    flash('Restaurante registrado sin publicar.', 'success')
    return redirect(url_for('owner.dashboard'), code=303)
