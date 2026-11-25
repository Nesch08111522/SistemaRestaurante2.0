# app/repositories/menus_diarios.py
"""
Repositorio de public.menus_diarios y sus tablas hijas.
Columnas del .sql (menus_diarios):
  id_menu, id_restaurante, fecha, tipo, precio, dia_semana,
  esta_activo, creado_en, actualizado_en

Columnas de menus_diarios_platos:
  id_menu, posicion, id_plato, nombre_plato_snapshot,
  precio_snapshot, categoria_snapshot, momento_comida

Columnas de menus_diarios_especiales:
  id_menu, posicion, descripcion
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class MenusDiariosRepository(PostgresRepository):
    table = "public.menus_diarios"
    columns = frozenset({
        "id_menu", "id_restaurante", "fecha", "tipo", "precio",
        "dia_semana", "esta_activo", "creado_en", "actualizado_en",
    })

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_menu=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def list_by_restaurante(
        cls, id_restaurante: int, *, only_active: bool = True
    ) -> list[dict[str, Any]]:
        where = "AND esta_activo=TRUE" if only_active else ""
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} "
                f"WHERE id_restaurante=%s {where} "
                f"ORDER BY fecha DESC, id_menu DESC",
                (int(id_restaurante),),
            )
            return list(cur.fetchall())

    @classmethod
    def list_by_fecha(
        cls, *, fecha: date, limit: int = 100
    ) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} "
                f"WHERE fecha=%s AND esta_activo=TRUE "
                f"ORDER BY id_restaurante LIMIT %s",
                (fecha, int(limit)),
            )
            return list(cur.fetchall())

    @classmethod
    def insert(
        cls,
        *,
        id_restaurante: int,
        fecha: date,
        tipo: str,
        precio: float = 0,
        dia_semana: str | None = None,
        esta_activo: bool = True,
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(id_restaurante, fecha, tipo, precio, dia_semana, esta_activo, "
                " creado_en, actualizado_en) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *",
                (
                    int(id_restaurante), fecha, tipo.strip(), precio,
                    dia_semana, bool(esta_activo), now, now,
                ),
            )
            return cur.fetchone()

    @classmethod
    def update_fields(cls, id_menu: int, values: dict[str, Any]) -> dict[str, Any] | None:
        allowed = cls.columns - {"id_menu", "creado_en"}
        payload = {k: v for k, v in values.items() if k in allowed}
        if not payload:
            return cls.get_by_id(id_menu)
        payload["actualizado_en"] = datetime.now(timezone.utc)
        names = list(payload)
        assignments = ",".join(f"{name}=%s" for name in names)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} SET {assignments} "
                f"WHERE id_menu=%s RETURNING *",
                tuple(payload[name] for name in names) + (int(id_menu),),
            )
            return cur.fetchone()


# ============================================================
# Tablas hijas
# ============================================================

class MenusDiariosPlatosRepository(PostgresRepository):
    table = "public.menus_diarios_platos"
    columns = frozenset({
        "id_menu", "posicion", "id_plato", "nombre_plato_snapshot",
        "precio_snapshot", "categoria_snapshot", "momento_comida",
    })

    @classmethod
    def list_for(cls, id_menu: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} "
                f"WHERE id_menu=%s ORDER BY posicion",
                (int(id_menu),),
            )
            return list(cur.fetchall())

    @classmethod
    def replace_for(cls, id_menu: int, platos: list[dict[str, Any]]) -> None:
        """
        Cada plato debe tener: nombre_plato_snapshot, precio_snapshot.
        Opcionales: id_plato, categoria_snapshot, momento_comida.
        """
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_menu=%s",
                (int(id_menu),),
            )
            pos = 0
            for p in platos:
                nombre = str(p.get("nombre_plato_snapshot") or "").strip()
                if not nombre:
                    continue
                try:
                    precio = float(p.get("precio_snapshot") or 0)
                except (TypeError, ValueError):
                    precio = 0
                pos += 1
                cur.execute(
                    f"INSERT INTO {cls.table} "
                    "(id_menu, posicion, id_plato, nombre_plato_snapshot, "
                    " precio_snapshot, categoria_snapshot, momento_comida) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (
                        int(id_menu), pos,
                        int(p["id_plato"]) if p.get("id_plato") else None,
                        nombre[:180], precio,
                        str(p.get("categoria_snapshot") or "")[:80] or None,
                        str(p.get("momento_comida") or "")[:40] or None,
                    ),
                )


class MenusDiariosEspecialesRepository(PostgresRepository):
    table = "public.menus_diarios_especiales"
    columns = frozenset({"id_menu", "posicion", "descripcion"})

    @classmethod
    def list_for(cls, id_menu: int) -> list[str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT descripcion FROM {cls.table} "
                f"WHERE id_menu=%s ORDER BY posicion",
                (int(id_menu),),
            )
            return [row["descripcion"] for row in cur.fetchall()]

    @classmethod
    def replace_for(cls, id_menu: int, especiales: list[str]) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_menu=%s",
                (int(id_menu),),
            )
            pos = 0
            for desc in especiales:
                clean = " ".join(str(desc).strip().split())
                if not clean:
                    continue
                pos += 1
                cur.execute(
                    f"INSERT INTO {cls.table} (id_menu, posicion, descripcion) "
                    f"VALUES (%s,%s,%s)",
                    (int(id_menu), pos, clean),
                )