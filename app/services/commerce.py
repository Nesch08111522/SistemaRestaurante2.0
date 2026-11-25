"""Relational checkout, stock and state machine. Amounts are Decimal soles, never floats."""
from datetime import datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from uuid import UUID
from app.models.company import permitted
from app.models.restaurant import RestaurantModel
from app.models.order import OrderModel
from app.repositories.pedidos_mercado import PedidosMercadoRepository
from app.repositories.operations import OperationsRepository as Repo, restaurant_transaction
from app.services.errors import DomainError

TRANSITIONS = {'pending': {'accepted','cancelled'}, 'accepted': {'preparing','cancelled'},
               'preparing': {'ready'}, 'ready': {'delivered'}, 'delivered': set(), 'cancelled': set()}


def integer(value, label, low=1, high=1000000):
    if type(value) is not int or not low <= value <= high:
        raise DomainError(f'{label}: usa un entero entre {low} y {high}.')
    return value


def money(value):
    try:
        if isinstance(value,bool): raise InvalidOperation
        amount=Decimal(str(value))
        if not amount.is_finite() or amount<0 or amount>Decimal('99999999') or amount!=amount.quantize(Decimal('.01')):
            raise InvalidOperation
        return amount.quantize(Decimal('.01'))
    except (InvalidOperation,TypeError,ValueError):
        raise DomainError('El importe debe ser válido y tener como máximo dos decimales.') from None


def authorize(user,rid,permission='orders.read.business'):
    restaurant=RestaurantModel.get_by_id(rid,full=False)
    if not restaurant: raise DomainError('Restaurante no encontrado.',404)
    if not permitted(user,restaurant['id_empresa'],permission):
        raise DomainError('Tu membresía o suscripción no permite esta operación.',403)
    return restaurant


def normalize_items(items):
    if not isinstance(items,list) or not 1<=len(items)<=40:
        raise DomainError('Selecciona entre 1 y 40 platos.')
    normalized=[]; seen=set()
    for item in items:
        if not isinstance(item,dict) or set(item)!={'dish_id','quantity'}:
            raise DomainError('Cada línea necesita plato y cantidad, sin precios enviados por el cliente.')
        pid=integer(item['dish_id'],'Plato');qty=integer(item['quantity'],'Cantidad',1,100)
        if pid in seen: raise DomainError('Combina las cantidades del mismo plato en una sola línea.')
        seen.add(pid);normalized.append({'dish_id':pid,'quantity':qty})
    return sorted(normalized,key=lambda x:x['dish_id'])


def checkout(user,data):
    allowed={'restaurant_id','items','channel','request_key','expected_total','destination'}
    if not isinstance(data,dict) or set(data)-allowed: raise DomainError('Solicitud de compra inválida.')
    rid=integer(data.get('restaurant_id'),'Restaurante')
    items=normalize_items(data.get('items'))
    if data.get('channel') not in {'Recojo','Local','Delivery'}: raise DomainError('Canal inválido.')
    destination=data.get('destination') or {}
    if not isinstance(destination,dict) or set(destination)-{'destinatario','telefono','direccion','distrito','ciudad','referencia'}:
        raise DomainError('Datos de entrega inválidos.')
    if any(not isinstance(v,str) or len(v)>240 for v in destination.values()): raise DomainError('Revisa los datos de entrega.')
    if data['channel']=='Delivery' and any(not destination.get(k,'').strip() for k in ['destinatario','telefono','direccion','distrito']):
        raise DomainError('Completa nombre, teléfono, dirección y distrito para delivery.')
    # Delivery service/fees are not configured in the existing env or restaurant contract.
    if data['channel']=='Delivery': raise DomainError('Este negocio todavía no tiene configurada la cotización de delivery.',409)
    try: key=f"web:{user['id']}:{UUID(str(data.get('request_key')))}"
    except (ValueError,TypeError,AttributeError): raise DomainError('Clave de solicitud inválida.') from None
    expected=money(data.get('expected_total'))
    fingerprint=sha256(json.dumps([rid,items,data['channel'],destination,str(expected)],sort_keys=True).encode()).hexdigest()
    with restaurant_transaction(rid, key):
        previous=PedidosMercadoRepository.get_by_clave_solicitud(key)
        if previous:
            control=Repo.control(previous['id_pedido'])
            if previous['id_usuario']!=user['id'] or previous['id_restaurante']!=rid or not control or control['hash_solicitud']!=fingerprint:
                raise DomainError('Esta solicitud ya se utilizó con otro contenido.',409)
            return previous
        restaurant=RestaurantModel.get_by_id(rid,full=False)
        if not restaurant or restaurant.get('estado_publicacion')!='published' or restaurant.get('suspendido') or restaurant.get('rechazado'):
            raise DomainError('El negocio no está disponible.',404)
        catalog={p['id_plato']:p for p in Repo.catalog(rid)}
        lines=[]; total=Decimal('0.00')
        for item in items:
            dish=catalog.get(item['dish_id'])
            if not dish or dish['stock']<item['quantity']:
                raise DomainError('Un plato dejó de estar disponible o no tiene suficientes porciones. Actualiza la carta.',409)
            price=money(dish['precio']);total+=price*item['quantity']
            lines.append(dict(id_plato=dish['id_plato'],nombre_snapshot=dish['nombre'],cantidad=item['quantity'],precio_unitario=price))
        total=money(total)
        if total!=expected: raise DomainError('El precio cambió. Actualiza la carta y revisa el total antes de confirmar.',409)
        order=OrderModel.create(id_restaurante=rid,id_usuario=user['id'],dia=datetime.now(timezone(timedelta(hours=-5))).date(),
            estado='pending',total=total,nombre_negocio_snapshot=restaurant['nombre'],canal=data['channel'],
            metodo_pago='Contraentrega',clave_solicitud=key,lineas=lines,destino=destination or None)
        for item in items:
            if not Repo.reserve(item['dish_id'],item['quantity'],order['id_pedido'],user['id']):
                raise DomainError('El stock cambió. No se creó el pedido; revisa las cantidades.',409)
        Repo.remember(order['id_pedido'],fingerprint);Repo.event(user['id'],rid,'pedido.creado',order['id_pedido'])
        return order


def change_status(user,order_id,target,expected,*,buyer=False):
    snapshot=OrderModel.get_by_id(order_id,full=False)
    if not snapshot: raise DomainError('Pedido no encontrado.',404)
    rid=snapshot['id_restaurante']
    with restaurant_transaction(rid):
        order=OrderModel.get_by_id(order_id,full=False)
        if buyer:
            if order['id_usuario']!=user['id']: raise DomainError('Pedido no encontrado.',404)
            if target!='cancelled' or order['estado'] not in {'pending','accepted','cancelled'}:
                raise DomainError('Este pedido ya no puede cancelarse desde tu cuenta.',409)
        else: authorize(user,rid,'orders.manage.business')
        if not Repo.control(order_id): raise DomainError('El pedido pertenece al flujo anterior; requiere revisión antes de operarlo.',409)
        if order['estado']==target: return order
        if order['estado']!=expected: raise DomainError('El estado cambió. Actualiza el pedido antes de actuar.',409)
        if target not in TRANSITIONS.get(order['estado'],set()): raise DomainError('Transición de estado no permitida.',409)
        if target=='cancelled' and order.get('pagado'): raise DomainError('Un pedido pagado requiere resolver el reembolso antes de cancelarlo.',409)
        if target=='cancelled': Repo.restore(order_id,user['id'])
        result=OrderModel.change_status(order_id,target)
        Repo.event(user['id'],rid,'pedido.'+target,order_id)
        return result


def adjust_stock(user,pid,quantity,version):
    from app.repositories.platos import PlatosRepository
    quantity=integer(quantity,'Porciones',0);version=integer(version,'Versión',0,2**63-1)
    dish=PlatosRepository.get_by_id(pid)
    if not dish: raise DomainError('Plato no encontrado.',404)
    rid=dish['id_restaurante']
    with restaurant_transaction(rid):
        authorize(user,rid,'inventory.manage')
        if not Repo.adjust(pid,quantity,version,user['id']): raise DomainError('El stock cambió desde que abriste la página. Actualízala.',409)
        Repo.event(user['id'],rid,'stock.ajustado')
