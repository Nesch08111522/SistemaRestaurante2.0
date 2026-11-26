# app/repositories/restaurantes.py
"""
Repositorio de public.restaurantes y sus tablas hijas.
Columnas del .sql (restaurantes):
  id_restaurante, id_empresa, id_propietario, id_categoria,
  nombre, descripcion, direccion, distrito, latitud, longitud,
  telefono, precio_promedio, calificacion, cantidad_resenas_reportada,
  hora_apertura, hora_cierre, url_imagen, promocion_texto,
  nombre_contacto_publicado, verificado, notas_moderacion, moderado_en,
  rechazado, suspendido, estado_aprobacion, estado_publicacion,
  modalidad_servicio, estado, tipo_cocina, tipo_menu, tipo_mercado,
  es_demo, empresa_demo, introduccion_menu
"""
from __future__ import annotations

from datetime import time
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class RestaurantesRepository(PostgresRepository):
    table = "public.restaurantes"
    columns = frozenset({
        "id_restaurante", "id_empresa", "id_propietario", "id_categoria",
        "nombre", "descripcion", "direccion", "distrito",
        "latitud", "longitud", "telefono", "precio_promedio",
        "calificacion", "cantidad_resenas_reportada",
        "hora_apertura", "hora_cierre", "url_imagen", "promocion_texto",
        "nombre_contacto_publicado", "verificado", "notas_moderacion",
        "moderado_en", "rechazado", "suspendido", "estado_aprobacion",
        "estado_publicacion", "modalidad_servicio", "estado",
        "tipo_cocina", "tipo_menu", "tipo_mercado", "es_demo",
        "empresa_demo", "introduccion_menu",
    })

    @classmethod
    def list_pending_review(cls):
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute("SELECT id_restaurante, id_empresa, nombre, estado, estado_publicacion "
                        "FROM public.restaurantes WHERE estado='pending_review' "
                        "ORDER BY id_restaurante LIMIT 200")
            return list(cur.fetchall())

    @classmethod
    def approve_and_publish(cls, restaurant_id):
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute("UPDATE public.restaurantes SET estado='active', estado_aprobacion='approved', "
                        "estado_publicacion='published', moderado_en=now() "
                        "WHERE id_restaurante=%s AND estado='pending_review' "
                        "AND NOT COALESCE(suspendido,false) AND NOT COALESCE(rechazado,false) RETURNING *",
                        (int(restaurant_id),))
            return cur.fetchone()

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_restaurante=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def list_by_empresa(cls, id_empresa: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_empresa=%s "
                f"ORDER BY id_restaurante",
                (int(id_empresa),),
            )
            return list(cur.fetchall())

    @classmethod
    def list_by_owner(cls, id_propietario: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_propietario=%s "
                f"ORDER BY id_restaurante",
                (int(id_propietario),),
            )
            return list(cur.fetchall())

    @classmethod
    def list_by_categoria(cls, id_categoria: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_categoria=%s "
                f"ORDER BY id_restaurante",
                (int(id_categoria),),
            )
            return list(cur.fetchall())

    @classmethod
    def list_published(cls, *, limit: int = 100) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} "
                f"WHERE estado_publicacion='published' "
                f"ORDER BY calificacion DESC NULLS LAST, id_restaurante "
                f"LIMIT %s",
                (int(limit),),
            )
            return list(cur.fetchall())

    @classmethod
    def insert(
        cls,
        *,
        id_empresa: int | None,
        id_propietario: int | None,
        id_categoria: int | None,
        nombre: str,
        descripcion: str | None = None,
        direccion: str | None = None,
        distrito: str | None = None,
        latitud: float | None = None,
        longitud: float | None = None,
        telefono: str | None = None,
        precio_promedio: float | None = None,
        calificacion: float | None = None,
        hora_apertura: time | None = None,
        hora_cierre: time | None = None,
        url_imagen: str | None = None,
        promocion_texto: str | None = None,
        estado: str = "pending_review",
        estado_publicacion: str = "unpublished",
        modalidad_servicio: str | None = None,
        tipo_cocina: str | None = None,
        tipo_menu: str | None = None,
        es_demo: bool = False,
        empresa_demo: str | None = None,
        introduccion_menu: str | None = None,
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.table}
                    (id_empresa, id_propietario, id_categoria, nombre,
                     descripcion, direccion, distrito, latitud, longitud,
                     telefono, precio_promedio, calificacion,
                     hora_apertura, hora_cierre, url_imagen, promocion_texto,
                     estado, estado_publicacion, modalidad_servicio,
                     tipo_cocina, tipo_menu, es_demo, empresa_demo, introduccion_menu)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING *
                """,
                (
                    id_empresa, id_propietario, id_categoria, nombre.strip(),
                    descripcion, direccion, distrito, latitud, longitud,
                    telefono, precio_promedio, calificacion,
                    hora_apertura, hora_cierre, url_imagen, promocion_texto,
                    estado, estado_publicacion, modalidad_servicio,
                    tipo_cocina, tipo_menu, bool(es_demo), empresa_demo,
                    introduccion_menu,
                ),
            )
            return cur.fetchone()

    @classmethod
    def update_fields(cls, id_restaurante: int, values: dict[str, Any]) -> dict[str, Any] | None:
        allowed = cls.columns - {"id_restaurante"}
        payload = {k: v for k, v in values.items() if k in allowed}
        if not payload:
            return cls.get_by_id(id_restaurante)
        names = list(payload)
        assignments = ",".join(f"{name}=%s" for name in names)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} SET {assignments} "
                f"WHERE id_restaurante=%s RETURNING *",
                tuple(payload[name] for name in names) + (int(id_restaurante),),
            )
            return cur.fetchone()


# ============================================================
# Tablas hijas (listas ordenadas por `posicion`)
# ============================================================

class RestaurantesEtiquetasRepository(PostgresRepository):
    table = "public.restaurantes_etiquetas"
    columns = frozenset({"id_restaurante", "posicion", "etiqueta"})

    @classmethod
    def list_for(cls, id_restaurante: int) -> list[str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT etiqueta FROM {cls.table} "
                f"WHERE id_restaurante=%s ORDER BY posicion",
                (int(id_restaurante),),
            )
            return [row["etiqueta"] for row in cur.fetchall()]

    @classmethod
    def replace_for(cls, id_restaurante: int, etiquetas: list[str]) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_restaurante=%s",
                (int(id_restaurante),),
            )
            pos = 0
            vistos = set()
            for etiqueta in etiquetas:
                clean = " ".join(str(etiqueta).strip().split())[:100]
                if not clean or clean in vistos:
                    continue
                vistos.add(clean)
                pos += 1
                cur.execute(
                    f"INSERT INTO {cls.table} (id_restaurante, posicion, etiqueta) "
                    f"VALUES (%s,%s,%s)",
                    (int(id_restaurante), pos, clean),
                )


class RestaurantesCaracteristicasRepository(PostgresRepository):
    table = "public.restaurantes_caracteristicas"
    columns = frozenset({"id_restaurante", "posicion", "caracteristica"})

    @classmethod
    def list_for(cls, id_restaurante: int) -> list[str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT caracteristica FROM {cls.table} "
                f"WHERE id_restaurante=%s ORDER BY posicion",
                (int(id_restaurante),),
            )
            return [row["caracteristica"] for row in cur.fetchall()]

    @classmethod
    def replace_for(cls, id_restaurante: int, caracteristicas: list[str]) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_restaurante=%s",
                (int(id_restaurante),),
            )
            pos = 0
            vistos = set()
            for c in caracteristicas:
                clean = " ".join(str(c).strip().split())[:120]
                if not clean or clean in vistos:
                    continue
                vistos.add(clean)
                pos += 1
                cur.execute(
                    f"INSERT INTO {cls.table} (id_restaurante, posicion, caracteristica) "
                    f"VALUES (%s,%s,%s)",
                    (int(id_restaurante), pos, clean),
                )


class RestaurantesRestriccionesDieteticasRepository(PostgresRepository):
    table = "public.restaurantes_restricciones_dieteticas"
    columns = frozenset({"id_restaurante", "posicion", "restriccion"})

    @classmethod
    def list_for(cls, id_restaurante: int) -> list[str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT restriccion FROM {cls.table} "
                f"WHERE id_restaurante=%s ORDER BY posicion",
                (int(id_restaurante),),
            )
            return [row["restriccion"] for row in cur.fetchall()]

    @classmethod
    def replace_for(cls, id_restaurante: int, restricciones: list[str]) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_restaurante=%s",
                (int(id_restaurante),),
            )
            pos = 0
            vistos = set()
            for r in restricciones:
                clean = " ".join(str(r).strip().split())[:120]
                if not clean or clean in vistos:
                    continue
                vistos.add(clean)
                pos += 1
                cur.execute(
                    f"INSERT INTO {cls.table} (id_restaurante, posicion, restriccion) "
                    f"VALUES (%s,%s,%s)",
                    (int(id_restaurante), pos, clean),
                )


class RestaurantesCanalesMercadoRepository(PostgresRepository):
    table = "public.restaurantes_canales_mercado"
    columns = frozenset({"id_restaurante", "posicion", "canal"})

    @classmethod
    def list_for(cls, id_restaurante: int) -> list[str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT canal FROM {cls.table} "
                f"WHERE id_restaurante=%s ORDER BY posicion",
                (int(id_restaurante),),
            )
            return [row["canal"] for row in cur.fetchall()]

    @classmethod
    def replace_for(cls, id_restaurante: int, canales: list[str]) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_restaurante=%s",
                (int(id_restaurante),),
            )
            pos = 0
            vistos = set()
            for c in canales:
                clean = " ".join(str(c).strip().split())[:80]
                if not clean or clean in vistos:
                    continue
                vistos.add(clean)
                pos += 1
                cur.execute(
                    f"INSERT INTO {cls.table} (id_restaurante, posicion, canal) "
                    f"VALUES (%s,%s,%s)",
                    (int(id_restaurante), pos, clean),
                )
