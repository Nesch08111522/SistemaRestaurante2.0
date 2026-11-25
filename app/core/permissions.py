# app/core/permissions.py
"""
Política declarativa de autorización de SmartResto.

La identidad de sesión autentica; este módulo decide qué operación puede
realizar cada rol. El alcance de negocio/sucursal se valida en company.py.
"""
from __future__ import annotations

from typing import FrozenSet


from app.core.roles import canonical_role

_PERMISSIONS: dict[str, FrozenSet[str]] = {
    "guest": frozenset({"catalog.read", "business.read", "profile.read.public"}),
    "diner": frozenset({
        "profile.read", "profile.update", "preferences.update", "favorites.manage",
        "orders.read.own", "reviews.create.own", "notifications.manage.own",
        "location.consent.manage", "rewards.read.own", "table.session.own",
    }),
    "business_owner": frozenset({
        "profile.read", "profile.update", "preferences.update", "business.manage",
        "branch.manage", "catalog.manage", "orders.read.business", "staff.invite",
        "staff.manage", "analytics.read.business", "audit.read.business",
        "notifications.manage.business", "rewards.manage.business",
        "tables.manage", "tables.service", "flow.manage", "loyalty.manage.business",
        "site.manage", "promotion.manage", "ai.business",
    }),
    "business_admin": frozenset({
        "profile.read", "profile.update", "business.read", "branch.manage",
        "catalog.manage", "orders.read.business", "staff.invite", "staff.manage",
        "analytics.read.business", "notifications.manage.business",
        "tables.manage", "tables.service", "flow.manage",
        "site.manage", "promotion.manage",
    }),
    "manager": frozenset({
        "profile.read", "profile.update", "branch.read", "catalog.manage",
        "orders.read.business", "staff.invite", "analytics.read.business",
        "tables.service", "flow.manage",
    }),
    "cashier": frozenset({
        "profile.read", "profile.update", "branch.read",
        "orders.read.business", "tables.service",
    }),
    "waiter": frozenset({
        "profile.read", "profile.update", "branch.read",
        "orders.read.business", "tables.service",
    }),
    "kitchen": frozenset({
        "profile.read", "profile.update", "branch.read", "orders.read.business",
    }),
    "admin": frozenset({
        "profile.read", "profile.update", "business.manage", "branch.manage",
        "catalog.manage", "platform.users.manage", "platform.roles.manage",
        "platform.verification.manage", "platform.moderation.manage",
        "platform.audit.read", "platform.settings.manage", "analytics.read.platform",
        "tables.manage", "tables.service", "flow.manage", "loyalty.manage.business",
        "site.manage", "promotion.manage", "ai.business",
    }),
}


# Operational capabilities are explicit; reading orders does not imply payment authority.
for _role in ('business_owner','business_admin','manager','kitchen','admin'):
    _PERMISSIONS[_role] = _PERMISSIONS[_role] | {'orders.manage.business'}
for _role in ('business_owner','business_admin','manager','admin'):
    _PERMISSIONS[_role] = _PERMISSIONS[_role] | {'inventory.manage'}


def _canonical_role(role: str | None) -> str:
    return canonical_role(role)


def permissions_for_role(role: str | None) -> list[str]:
    return sorted(_PERMISSIONS.get(_canonical_role(role), frozenset()))


def can(role: str | None, permission: str) -> bool:
    return permission in _PERMISSIONS.get(_canonical_role(role), frozenset())