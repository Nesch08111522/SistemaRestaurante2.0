"""Validate editable restaurant fields; ownership and publication are never inputs."""
from datetime import time
from decimal import Decimal, InvalidOperation
from urllib.parse import urlsplit
from app.blueprints.workspace import WorkspaceError

MODES = {'pickup_only':'Solo recojo', 'dine_in_only':'Atención en local',
         'dine_in_and_delivery':'Local y delivery', 'delivery_only':'Solo delivery'}
LISTS = ('etiquetas','caracteristicas','restricciones_dieteticas')


def clean(form, name, limit, required=False):
    value = str(form.get(name, '')).strip()
    if len(value) > limit or (required and not value):
        raise WorkspaceError(f'Revisa {name.replace("_", " ")}: máximo {limit} caracteres.')
    return value


def parse(form):
    fields = {key: clean(form,key,limit,required) or None for key,limit,required in [
        ('direccion',250,False),('distrito',100,True),('telefono',40,False),
        ('descripcion',3000,False),('url_imagen',1000,False),('promocion_texto',250,False),
        ('tipo_cocina',100,False)]}
    fields['nombre'] = clean(form,'restaurante',120,True)
    if len(fields['nombre']) < 2:
        raise WorkspaceError('El nombre del restaurante debe tener al menos 2 caracteres.')
    fields['modalidad_servicio'] = form.get('modalidad_servicio') or 'dine_in_only'
    if fields['modalidad_servicio'] not in MODES:
        raise WorkspaceError('Selecciona una modalidad de atención válida.')
    menu = form.get('tipo_menu') or 'mixed'
    if menu not in {'daily','a_la_carte','mixed'}:
        raise WorkspaceError('Selecciona un tipo de carta válido.')
    fields['tipo_menu'] = menu
    try:
        raw = form.get('id_categoria')
        fields['id_categoria'] = int(raw) if raw else None
        if fields['id_categoria'] is not None and fields['id_categoria'] <= 0:
            raise ValueError()
    except (ValueError,TypeError):
        raise WorkspaceError('Selecciona una categoría válida.') from None
    price = form.get('precio_promedio')
    try:
        amount = Decimal(price) if price else None
        if amount is not None and (not amount.is_finite() or not 0 <= amount <= 999999 or amount != amount.quantize(Decimal('.01'))):
            raise ValueError()
        fields['precio_promedio'] = amount
    except (InvalidOperation,ValueError,TypeError):
        raise WorkspaceError('El precio promedio debe ser positivo, con hasta dos decimales.') from None
    for key in ('hora_apertura','hora_cierre'):
        value = form.get(key)
        try:
            fields[key] = time.fromisoformat(value) if value else None
        except ValueError:
            raise WorkspaceError('Revisa los horarios de apertura y cierre.') from None
    if bool(fields['hora_apertura']) != bool(fields['hora_cierre']):
        raise WorkspaceError('Completa ambos horarios o deja ambos vacíos.')
    if fields['url_imagen']:
        try:
            url = urlsplit(fields['url_imagen'])
            if url.scheme != 'https' or not url.hostname or url.username or url.password:
                raise ValueError()
        except ValueError:
            raise WorkspaceError('La portada debe usar una dirección HTTPS válida.') from None
    lat, lon = form.get('latitud'), form.get('longitud')
    fields['latitud'] = fields['longitud'] = None
    if form.get('solo_distrito') == 'on':
        fields['direccion'] = None
    else:
        if not fields['direccion']:
            raise WorkspaceError('Indica una dirección o elige publicar solo el distrito.')
        if bool(lat) != bool(lon):
            raise WorkspaceError('Completa ambas coordenadas o elimina el punto del mapa.')
        if lat:
            try:
                latitude, longitude = Decimal(lat), Decimal(lon)
                if not latitude.is_finite() or not longitude.is_finite() or not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
                    raise ValueError()
                fields.update(latitud=latitude, longitud=longitude)
            except (InvalidOperation,ValueError):
                raise WorkspaceError('Las coordenadas no son válidas.') from None
    lists = {}
    for key in LISTS:
        if key in form:
            values = list(dict.fromkeys(x.strip() for x in clean(form,key,2500).replace('\n',',').split(',') if x.strip()))
            if len(values) > 20 or any(len(x)>100 for x in values):
                raise WorkspaceError('Usa hasta 20 etiquetas por campo, de máximo 100 caracteres.')
            lists[key] = values
    return fields, lists
