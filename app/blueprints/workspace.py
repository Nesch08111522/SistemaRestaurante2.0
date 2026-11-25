"""Shared HTTP/UI helpers for private blueprints; no persistence or business rules."""
from functools import wraps
from flask import abort, current_app, g, jsonify, render_template, request, url_for
from psycopg import IntegrityError, OperationalError
from psycopg.errors import UndefinedTable, UndefinedColumn
from app.services.errors import DomainError
from app.core.security import fresh_session_user
from app.db.connection import DatabaseConfigurationError, DatabaseConnectionError


class WorkspaceError(Exception):
    def __init__(self, message, status=400):
        self.message, self.status = message, status


def workspace_errors(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (WorkspaceError, DomainError) as error:
            message, status = error.message, error.status
        except (UndefinedTable, UndefinedColumn):
            g.database_unavailable = True
            message, status = "Esta función todavía no está habilitada. El equipo debe completar su preparación antes de utilizarla.", 503
        except IntegrityError:
            message, status = "No se pudo guardar: los datos ya existen o tienen una relación incompatible.", 409
        except (DatabaseConfigurationError, DatabaseConnectionError, OperationalError):
            g.database_unavailable = True
            message, status = "No podemos acceder a tus datos en este momento. Inténtalo nuevamente.", 503
        if request.is_json or "/api/" in request.path:
            response = jsonify(success=False, error=message)
        else:
            response = current_app.make_response(render_template("workspace/error.html", message=message, status=status))
        response.status_code = status
        if status == 503:
            response.headers["Retry-After"] = "30"
        return response
    return wrapped


def actor():
    user = fresh_session_user()
    if not user:
        abort(401)
    return user


def body(allowed):
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise WorkspaceError("Se requiere un objeto JSON.")
    if set(data) - set(allowed):
        raise WorkspaceError("La solicitud contiene campos no permitidos.")
    return data


def text(value, label, maximum, *, required=False):
    if not isinstance(value, str) or len(value) > maximum or (required and not value.strip()):
        raise WorkspaceError(f"Revisa {label} (máximo {maximum} caracteres).")
    return value.strip()


def positive_id(value):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise WorkspaceError("El identificador debe ser un entero positivo.")
    return value


def navigation():
    user = fresh_session_user() if not getattr(g, 'database_unavailable', False) else None
    role = (user or {}).get('role', 'guest')
    business = role in {'business_owner', 'business_admin', 'manager', 'admin'}
    service = business or role in {'cashier', 'waiter'}
    kitchen = business or role == 'kitchen'
    groups = [ ('MI EXPERIENCIA', [
        ('auth.workspace_home', 'Mi inicio', 'home', True),
        ('market.checkout', 'Hacer un pedido', 'menu', True),
        ('market.orders', 'Mis pedidos', 'orders', True),
        ('auth.favorites', 'Favoritos', 'heart', True),
        ('auth.history', 'Mi historial', 'clock', True),
        ('auth.reviews', 'Mis reseñas', 'star', True)]),
        ('CENTRO DE CONTROL', [
        ('owner.dashboard', 'Mi empresa', 'business', business),
        ('ar.manage', 'Catálogo y Menú 3D', 'menu', business),
        ('owner.orders', 'Pedidos del negocio', 'orders', business),
        ('salon.index', 'Salón y mesas', 'grid', service),
        ('kitchen.index', 'Cocina', 'kitchen', kitchen),
        ('owner.audit_menu', 'Auditar mi carta', 'spark', business)]),
        ('CONTROL GLOBAL', [
        ('admin.dashboard', 'Dashboard global', 'grid', role == 'admin'),
        ('admin.users', 'Usuarios', 'user', role == 'admin'),
        ('admin.moderations', 'Moderación', 'shield', role == 'admin')]),
        ('MI CUENTA', [
        ('auth.notifications', 'Notificaciones', 'bell', True),
        ('auth.profile', 'Mi perfil', 'user', True),
        ('loyalty.index', 'Mis puntos', 'star', True),
        ('pantry.index', 'Cocina en casa', 'kitchen', True)])]
    return [(title, [(url_for(ep), label, icon, ep == request.endpoint) for ep,label,icon,allowed in entries
                     if allowed and ep in current_app.view_functions]) for title,entries in groups]
