"""Business registration and tenant-scoped restaurant editing."""
from uuid import uuid4
from flask import flash, g, redirect, request, url_for, render_template
from app.core.auth_guard import empresa_required, login_required, role_required
from app.blueprints.workspace import actor, text, workspace_errors, WorkspaceError
from app.db.repository import shared_transaction
from app.models.company import create_company_with_owner, get_company_for_user, permitted
from app.repositories.categorias import CategoriasRepository
from app.repositories.restaurantes import (RestaurantesRepository, RestaurantesEtiquetasRepository,
    RestaurantesCaracteristicasRepository, RestaurantesRestriccionesDieteticasRepository)
from app.services.business_registration import parse, MODES
from . import bp

LIST_REPOS = {'etiquetas':RestaurantesEtiquetasRepository,
              'caracteristicas':RestaurantesCaracteristicasRepository,
              'restricciones_dieteticas':RestaurantesRestriccionesDieteticasRepository}


def registration_form(values=None, error=None, status=200, restaurant=None, new_company=True):
    return render_template('owner/setup.html', values=values or {}, error=error,
        categories=CategoriasRepository.list_all(), modes=MODES, restaurant=restaurant,
        new_company=new_company), status


def restaurant_fields():
    fields, lists = parse(request.form)
    if fields['id_categoria'] and not CategoriasRepository.get_by_id(fields['id_categoria']):
        raise WorkspaceError('La categoría seleccionada ya no está disponible.')
    return fields, lists


def save_lists(rid, values):
    for key, items in values.items():
        LIST_REPOS[key].replace_for(rid, items)


@bp.post('/registrar')
@workspace_errors
@login_required
@role_required('business_owner')
def create_business():
    user = actor()
    try:
        name = text(request.form.get('empresa'), 'empresa', 120, required=True)
        if len(name) < 2:
            raise WorkspaceError('El nombre de la empresa debe tener al menos 2 caracteres.')
        fields, lists = restaurant_fields()
    except WorkspaceError as error:
        return registration_form(request.form, error.message, error.status)
    with shared_transaction() as conn, conn.cursor() as cur:
        cur.execute('SELECT id_usuario FROM public.usuarios WHERE id_usuario=%s FOR UPDATE', (user['id'],))
        if get_company_for_user(user['id']):
            return redirect(url_for('owner.dashboard'), code=303)
        company = create_company_with_owner(owner_user_id=user['id'],
            identificador_url='negocio-' + uuid4().hex, nombre=name, plan='basic')
        restaurant = RestaurantesRepository.insert(id_empresa=company['id_empresa'], id_propietario=user['id'], **fields)
        if lists:
            save_lists(restaurant['id_restaurante'], lists)
    flash('Empresa y restaurante registrados. Tu ficha está guardada y todavía no es pública.', 'success')
    return redirect(url_for('owner.dashboard'), code=303)


@bp.route('/restaurantes/nuevo', methods=['GET'])
@workspace_errors
@login_required
@role_required('business_owner','business_admin','manager')
@empresa_required
def new_restaurant():
    if not permitted(actor(), g.empresa['id_empresa'], 'branch.manage'):
        raise WorkspaceError('Tu membresía no permite registrar restaurantes.', 403)
    return registration_form(new_company=False)


@bp.post('/restaurantes')
@workspace_errors
@login_required
@role_required('business_owner','business_admin','manager')
@empresa_required
def create_restaurant():
    user = actor()
    if not permitted(user, g.empresa['id_empresa'], 'branch.manage'):
        raise WorkspaceError('Tu membresía no permite registrar restaurantes.', 403)
    try:
        fields, lists = restaurant_fields()
    except WorkspaceError as error:
        return registration_form(request.form,error.message,error.status,new_company=False)
    with shared_transaction():
        restaurant = RestaurantesRepository.insert(id_empresa=g.empresa['id_empresa'], id_propietario=user['id'], **fields)
        if lists:
            save_lists(restaurant['id_restaurante'], lists)
    flash('Restaurante registrado sin publicar.', 'success')
    return redirect(url_for('owner.dashboard'), code=303)


@bp.route('/restaurantes/<int:restaurant_id>/editar', methods=['GET','POST'])
@workspace_errors
@login_required
@role_required('business_owner','business_admin','manager')
@empresa_required
def edit_restaurant(restaurant_id):
    restaurant = RestaurantesRepository.get_by_id(restaurant_id)
    if not restaurant or restaurant['id_empresa'] != g.empresa['id_empresa']:
        raise WorkspaceError('Restaurante no encontrado.',404)
    if not permitted(actor(),g.empresa['id_empresa'],'catalog.manage'):
        raise WorkspaceError('Tu membresía no permite editar este restaurante.',403)
    if request.method == 'POST':
        try:
            fields, lists = restaurant_fields()
        except WorkspaceError as error:
            return registration_form(request.form,error.message,error.status,restaurant,False)
        with shared_transaction():
            RestaurantesRepository.update_fields(restaurant_id,fields)
            save_lists(restaurant_id,lists)
        flash('Ficha del restaurante actualizada.', 'success')
        return redirect(url_for('owner.dashboard'),code=303)
    values = {key: value if value is not None else '' for key,value in restaurant.items()}
    values['restaurante'] = restaurant['nombre']
    values['solo_distrito'] = 'on' if not restaurant.get('direccion') else ''
    for key,repo in LIST_REPOS.items():
        values[key] = ', '.join(repo.list_for(restaurant_id))
    return registration_form(values,restaurant=restaurant,new_company=False)
