# app/repositories/usuarios.py
"""
Repositorio de la tabla public.usuarios y sus tablas hijas.
Basado en SmartRestoBD_relacional_v2.sql.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


# ============================================================
# TABLA PRINCIPAL: usuarios
# ============================================================

class UsuariosRepository(PostgresRepository):
    """
    Columnas según el .sql:
      id_usuario, nombre_usuario, hash_contrasena, rol, nombre_mostrar,
      correo, estado_cuenta, empresa_demo, activacion_pendiente,
      creado_en, actualizado_en
    """
    table = "public.usuarios"
    columns = frozenset({
        "id_usuario", "nombre_usuario", "hash_contrasena", "rol",
        "nombre_mostrar", "correo", "estado_cuenta", "empresa_demo",
        "activacion_pendiente", "creado_en", "actualizado_en",
    })

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_usuario=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def get_by_username(cls, username: str) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} "
                f"WHERE nombre_usuario=%s ORDER BY id_usuario LIMIT 1",
                (username,),
            )
            return cur.fetchone()

    @classmethod
    def get_by_login(cls, identifier: str) -> dict[str, Any] | None:
        """Exact username takes precedence; email must identify one account."""
        identifier = identifier.strip()
        if not identifier:
            return None
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} "
                "WHERE nombre_usuario=%s OR lower(correo)=lower(%s) "
                "ORDER BY (nombre_usuario=%s) DESC, id_usuario LIMIT 2",
                (identifier, identifier, identifier),
            )
            rows = list(cur.fetchall())
        exact = [row for row in rows if row["nombre_usuario"] == identifier]
        if exact:
            return exact[0]
        return rows[0] if len(rows) == 1 else None

    @classmethod
    def get_by_email(cls, email: str) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE correo=%s ORDER BY id_usuario",
                (email.lower(),),
            )
            return list(cur.fetchall())

    @classmethod
    def list_by_role(cls, role: str, *, limit: int = 200) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE rol=%s "
                f"ORDER BY id_usuario LIMIT %s",
                (role, int(limit)),
            )
            return list(cur.fetchall())

    @classmethod
    def insert(
        cls,
        *,
        nombre_usuario: str,
        hash_contrasena: str,
        rol: str,
        nombre_mostrar: str | None = None,
        correo: str | None = None,
        estado_cuenta: str | None = None,
        empresa_demo: str | None = None,
        activacion_pendiente: bool = False,
    ) -> dict[str, Any]:
        """Inserta un usuario. El id_usuario se genera por secuencia."""
        now = datetime.now(timezone.utc)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(nombre_usuario, hash_contrasena, rol, nombre_mostrar, correo, "
                " estado_cuenta, empresa_demo, activacion_pendiente, creado_en, actualizado_en) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *",
                (
                    nombre_usuario, hash_contrasena, rol, nombre_mostrar,
                    (correo or "").lower() or None, estado_cuenta,
                    empresa_demo, bool(activacion_pendiente), now, now,
                ),
            )
            return cur.fetchone()

    @classmethod
    def update_fields(cls, id_usuario: int, values: dict[str, Any]) -> dict[str, Any] | None:
        allowed = cls.columns - {"id_usuario", "creado_en"}
        payload = {k: v for k, v in values.items() if k in allowed}
        if not payload:
            return cls.get_by_id(id_usuario)
        payload["actualizado_en"] = datetime.now(timezone.utc)
        names = list(payload)
        assignments = ",".join(f"{name}=%s" for name in names)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} SET {assignments} "
                f"WHERE id_usuario=%s RETURNING *",
                tuple(payload[name] for name in names) + (int(id_usuario),),
            )
            return cur.fetchone()

    @classmethod
    def set_password_hash(cls, id_usuario: int, hash_contrasena: str) -> None:
        cls.update_fields(id_usuario, {"hash_contrasena": hash_contrasena})

    @classmethod
    def bump_auth_epoch_placeholder(cls, id_usuario: int) -> None:
        """
        El .sql no tiene columna auth_epoch. Se deja marcado para futura migración.
        Por ahora, actualizar `actualizado_en` es suficiente para invalidar caches.
        """
        cls.update_fields(id_usuario, {})


# ============================================================
# TABLA HIJA: usuarios_preferencias
# ============================================================

class UsuariosPreferenciasRepository(PostgresRepository):
    table = "public.usuarios_preferencias"
    columns = frozenset({"id_usuario", "preferencia"})

    @classmethod
    def list_for_user(cls, id_usuario: int) -> list[str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT preferencia FROM {cls.table} "
                f"WHERE id_usuario=%s ORDER BY preferencia",
                (int(id_usuario),),
            )
            return [row["preferencia"] for row in cur.fetchall()]

    @classmethod
    def replace_for_user(cls, id_usuario: int, preferencias: list[str]) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_usuario=%s",
                (int(id_usuario),),
            )
            for pref in preferencias:
                clean = " ".join(str(pref).strip().split()).lower()[:120]
                if not clean:
                    continue
                cur.execute(
                    f"INSERT INTO {cls.table} (id_usuario, preferencia) "
                    f"VALUES (%s,%s) ON CONFLICT DO NOTHING",
                    (int(id_usuario), clean),
                )


# ============================================================
# TABLA HIJA: usuarios_restricciones
# ============================================================

class UsuariosRestriccionesRepository(PostgresRepository):
    table = "public.usuarios_restricciones"
    columns = frozenset({"id_usuario", "restriccion"})

    RESTRICCIONES_VALIDAS = frozenset({
        "vegano", "vegetariano", "celiaco", "sin gluten", "alergia mariscos",
    })

    @classmethod
    def list_for_user(cls, id_usuario: int) -> list[str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT restriccion FROM {cls.table} "
                f"WHERE id_usuario=%s ORDER BY restriccion",
                (int(id_usuario),),
            )
            return [row["restriccion"] for row in cur.fetchall()]

    @classmethod
    def replace_for_user(cls, id_usuario: int, restricciones: list[str]) -> None:
        limpio = [
            " ".join(str(r).strip().split()).lower()
            for r in restricciones
            if " ".join(str(r).strip().split()).lower() in cls.RESTRICCIONES_VALIDAS
        ]
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_usuario=%s",
                (int(id_usuario),),
            )
            for r in set(limpio):
                cur.execute(
                    f"INSERT INTO {cls.table} (id_usuario, restriccion) "
                    f"VALUES (%s,%s) ON CONFLICT DO NOTHING",
                    (int(id_usuario), r),
                )


# ============================================================
# TABLA HIJA: usuarios_detalles_negocio
# ============================================================

class UsuariosDetallesNegocioRepository(PostgresRepository):
    table = "public.usuarios_detalles_negocio"
    columns = frozenset({"id_usuario", "nombre_negocio", "telefono", "distrito"})

    @classmethod
    def get_for_user(cls, id_usuario: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_usuario=%s",
                (int(id_usuario),),
            )
            return cur.fetchone()

    @classmethod
    def upsert_for_user(
        cls,
        id_usuario: int,
        *,
        nombre_negocio: str | None = None,
        telefono: str | None = None,
        distrito: str | None = None,
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.table} (id_usuario, nombre_negocio, telefono, distrito)
                VALUES (%s,%s,%s,%s)
                ON CONFLICT (id_usuario) DO UPDATE
                SET nombre_negocio = EXCLUDED.nombre_negocio,
                    telefono = EXCLUDED.telefono,
                    distrito = EXCLUDED.distrito
                RETURNING *
                """,
                (int(id_usuario), nombre_negocio, telefono, distrito),
            )
            return cur.fetchone()