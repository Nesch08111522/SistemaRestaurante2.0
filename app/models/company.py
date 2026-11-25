# app/models/company.py
"""
CompanyModel relacional (Fase 2).

Reemplaza al modelo basado en sr_businesses + app_records.

Responsabilidades:
- Empresa, sucursal, membresía y suscripción en tablas relacionales.
- Lógica de permisos por suscripción (`permitted`) basada en el .sql.
- Validación de `subscription_allows()` con `empresas_suscripciones`.
"""
from __future__ import annotations

from datetime import date
from typing import Any

from app.core.permissions import can
from app.repositories.empresas import EmpresasRepository
from app.repositories.empresas_suscripciones import EmpresasSuscripcionesRepository
from app.repositories.membresias import MembresiasRepository
from app.repositories.sucursales import SucursalesRepository
from app.repositories.usuarios import UsuariosRepository


PLANS = ("basic", "decente", "premium")
LEVELS = dict(zip(PLANS, range(3)))

CAPABILITIES = {
    "orders.manage.business": 0, "inventory.manage": 0,
    "business.manage": 0, "branch.manage": 0, "catalog.manage": 0,
    "orders.read.business": 0, "notifications.manage.business": 0,
    "tables.service": 0, "tables.manage": 1, "staff.manage": 1,
    "staff.invite": 1, "analytics.read.business": 1, "promotion.manage": 1,
    "site.manage": 1, "flow.manage": 2, "loyalty.manage.business": 2,
    "rewards.manage.business": 2, "audit.read.business": 2, "ai.business": 2,
}


def subscription_allows(
    id_empresa: int, permission: str
) -> bool:
    """
    Determina si la suscripción de la empresa permite un permiso.

    Reglas:
    - Empresa existe y `estado='active'`.
    - Suscripción existe y `estado='active'`.
    - `vence_el` no ha pasado (si está definido).
    - El permiso no está en módulos desactivados.
    - El nivel del plan >= nivel del permiso.
    """
    empresa = EmpresasRepository.get_by_id(id_empresa)
    if not empresa or empresa.get("estado") != "active":
        return False

    sub = EmpresasSuscripcionesRepository.get_by_empresa(id_empresa)
    if not sub or sub.get("estado") != "active":
        return False

    vence = sub.get("vence_el")
    if vence:
        try:
            if isinstance(vence, str):
                vence = date.fromisoformat(vence)
            if vence < date.today():
                return False
        except (TypeError, ValueError):
            return False

    disabled = EmpresasSuscripcionesRepository.get_disabled_modules(id_empresa)
    if permission in disabled:
        return False

    plan = sub.get("plan")
    if plan not in LEVELS:
        return False

    return LEVELS[plan] >= CAPABILITIES.get(permission, 99)


def permitted(user: dict | None, id_empresa: int, permission: str) -> bool:
    """
    Determina si el usuario puede ejecutar `permission` sobre la empresa.

    Reglas:
    - Usuario activo.
    - Admin de plataforma: bypass total.
    - Si es owner directo en `empresas` (por membresía `business_owner`):
      debe cumplir `subscription_allows`.
    - Si tiene otra membresía activa: debe tener el rol que otorga
      el permiso + `subscription_allows`.
    """
    if not user:
        return False

    account = UsuariosRepository.get_by_id(user["id"])
    if not account:
        return False

    from app.models.user import UserModel
    if not UserModel.is_active(account):
        return False

    if account.get("rol") == "admin":
        return True

    membership = MembresiasRepository.get_for_user_empresa(
        account["id_usuario"], id_empresa
    )
    if not membership or membership.get("estado") != "active":
        return False

    if not subscription_allows(id_empresa, permission):
        return False

    return can(membership["rol"], permission)


def get_company_for_user(user_id: int) -> dict[str, Any] | None:
    """
    Devuelve la primera empresa activa del usuario con su suscripción y sucursales.
    Para cuando el usuario solo tiene una empresa (caso típico).
    """
    membresias = MembresiasRepository.list_by_usuario(user_id)
    if not membresias:
        return None

    primera = membresias[0]
    id_empresa = primera["id_empresa"]
    empresa = EmpresasRepository.get_by_id(id_empresa)
    if not empresa:
        return None

    suscripcion = EmpresasSuscripcionesRepository.get_by_empresa(id_empresa) or {}
    sucursales = SucursalesRepository.list_by_empresa(id_empresa)
    modulos_desactivados = EmpresasSuscripcionesRepository.get_disabled_modules(id_empresa)

    return {
        **empresa,
        "membresia": primera,
        "suscripcion": suscripcion,
        "sucursales": sucursales,
        "modulos_desactivados": modulos_desactivados,
    }


def create_company_with_owner(
    *,
    owner_user_id: int,
    identificador_url: str,
    nombre: str,
    plan: str = "basic",
) -> dict[str, Any]:
    """
    Crea una empresa + membresía business_owner + suscripción en una sola transacción.
    Devuelve la empresa recién creada con sus datos extendidos.
    """
    if plan not in PLANS:
        raise ValueError(f"Plan inválido: {plan}")

    empresa = EmpresasRepository.insert(
        identificador_url=identificador_url,
        nombre=nombre,
        estado="active",
        es_demo=False,
        origen_alta="companies-v1",
    )
    id_empresa = empresa["id_empresa"]

    MembresiasRepository.insert(
        id_usuario=owner_user_id,
        id_empresa=id_empresa,
        rol="business_owner",
        estado="active",
    )
    EmpresasSuscripcionesRepository.upsert_for_empresa(
        id_empresa=id_empresa,
        plan=plan,
        estado="active",
        revision=1,
    )
    return get_company_for_user(owner_user_id) or empresa


def change_subscription(
    *,
    actor_user_id: int,
    id_empresa: int,
    plan: str,
    estado: str,
    inicia_el: date | None = None,
    vence_el: date | None = None,
    disabled: list[str] | None = None,
) -> dict[str, Any]:
    """
    Cambia la suscripción de una empresa. Solo admins.
    """
    actor = UsuariosRepository.get_by_id(actor_user_id)
    if not actor or actor.get("rol") != "admin":
        raise PermissionError("Administrador requerido.")

    if plan not in PLANS:
        raise ValueError("Plan inválido.")
    if estado not in ("active", "suspended"):
        raise ValueError("Estado inválido.")

    if inicia_el and vence_el and vence_el < inicia_el:
        raise ValueError("Vencimiento anterior a contratación.")

    if disabled is not None:
        desconocidos = set(disabled) - set(CAPABILITIES.keys())
        if desconocidos:
            raise ValueError(f"Capacidad desconocida: {sorted(desconocidos)}")

    EmpresasSuscripcionesRepository.upsert_for_empresa(
        id_empresa=id_empresa,
        plan=plan,
        estado=estado,
        inicia_el=inicia_el,
        vence_el=vence_el,
    )
    if disabled is not None:
        EmpresasSuscripcionesRepository.set_disabled_modules(id_empresa, disabled)

    return EmpresasSuscripcionesRepository.get_by_empresa(id_empresa) or {}