# app/repositories/platos.py
"""
Repositorio de public.platos y sus tablas hijas.
Columnas del .sql (platos):
  id_plato, id_restaurante, nombre, descripcion, precio, categoria,
  fecha_menu, dia_semana, momento_comida, tiempo_preparacion_minutos,
  nivel_picante, es_temporal, esta_disponible, es_recomendado, creado_en
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class PlatosRepository(PostgresRepository):
    table = "public.platos"
    columns = frozenset({
        "id_plato", "id_restaurante", "nombre", "descripcion", "precio",
        "categoria", "fecha_menu", "dia_semana", "momento_comida",
        "tiempo_preparacion_minutos", "nivel_picante", "es_temporal",
        "esta_disponible", "es_recomendado", "creado_en",
    })

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_plato=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def list_by_restaurante(
        cls, id_restaurante: int, *, only_available: bool = False
    ) -> list[dict[str, Any]]:
        where = "AND esta_disponible=TRUE" if only_available else ""
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} "
                f"WHERE id_restaurante=%s {where} ORDER BY id_plato",
                (int(id_restaurante),),
            )
            return list(cur.fetchall())

    @classmethod
    def list_by_categoria_plato(
        cls, categoria: str, *, limit: int = 200
    ) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} "
                f"WHERE categoria=%s AND esta_disponible=TRUE "
                f"ORDER BY id_plato LIMIT %s",
                (categoria.strip(), int(limit)),
            )
            return list(cur.fetchall())

    @classmethod
    def insert(
        cls,
        *,
        id_restaurante: int,
        nombre: str,
        precio: float,
        categoria: str | None = None,
        descripcion: str | None = None,
        fecha_menu: date | None = None,
        dia_semana: str | None = None,
        momento_comida: str | None = None,
        tiempo_preparacion_minutos: int | None = None,
        nivel_picante: int | None = None,
        es_temporal: bool | None = None,
        esta_disponible: bool = True,
        es_recomendado: bool = False,
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.table}
                    (id_restaurante, nombre, precio, categoria, descripcion,
                     fecha_menu, dia_semana, momento_comida,
                     tiempo_preparacion_minutos, nivel_picante, es_temporal,
                     esta_disponible, es_recomendado, creado_en)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING *
                """,
                (
                    int(id_restaurante), nombre.strip(), precio, categoria,
                    descripcion, fecha_menu, dia_semana, momento_comida,
                    tiempo_preparacion_minutos, nivel_picante, es_temporal,
                    bool(esta_disponible), bool(es_recomendado),
                    datetime.now(timezone.utc),
                ),
            )
            return cur.fetchone()

    @classmethod
    def update_fields(cls, id_plato: int, values: dict[str, Any]) -> dict[str, Any] | None:
        allowed = cls.columns - {"id_plato", "creado_en"}
        payload = {k: v for k, v in values.items() if k in allowed}
        if not payload:
            return cls.get_by_id(id_plato)
        names = list(payload)
        assignments = ",".join(f"{name}=%s" for name in names)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} SET {assignments} "
                f"WHERE id_plato=%s RETURNING *",
                tuple(payload[name] for name in names) + (int(id_plato),),
            )
            return cur.fetchone()


# ============================================================
# Tablas hijas
# ============================================================

class PlatosEtiquetasRepository(PostgresRepository):
    table = "public.platos_etiquetas"
    columns = frozenset({"id_plato", "posicion", "etiqueta"})

    @classmethod
    def list_for(cls, id_plato: int) -> list[str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT etiqueta FROM {cls.table} "
                f"WHERE id_plato=%s ORDER BY posicion",
                (int(id_plato),),
            )
            return [row["etiqueta"] for row in cur.fetchall()]

    @classmethod
    def replace_for(cls, id_plato: int, etiquetas: list[str]) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_plato=%s",
                (int(id_plato),),
            )
            pos = 0
            for etiqueta in etiquetas:
                clean = " ".join(str(etiqueta).strip().split())[:100]
                if not clean:
                    continue
                pos += 1
                cur.execute(
                    f"INSERT INTO {cls.table} (id_plato, posicion, etiqueta) "
                    f"VALUES (%s,%s,%s)",
                    (int(id_plato), pos, clean),
                )


class PlatosIngredientesRepository(PostgresRepository):
    table = "public.platos_ingredientes"
    columns = frozenset({"id_plato", "posicion", "ingrediente"})

    @classmethod
    def list_for(cls, id_plato: int) -> list[str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT ingrediente FROM {cls.table} "
                f"WHERE id_plato=%s ORDER BY posicion",
                (int(id_plato),),
            )
            return [row["ingrediente"] for row in cur.fetchall()]

    @classmethod
    def replace_for(cls, id_plato: int, ingredientes: list[str]) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_plato=%s",
                (int(id_plato),),
            )
            pos = 0
            for ing in ingredientes:
                clean = " ".join(str(ing).strip().split())[:160]
                if not clean:
                    continue
                pos += 1
                cur.execute(
                    f"INSERT INTO {cls.table} (id_plato, posicion, ingrediente) "
                    f"VALUES (%s,%s,%s)",
                    (int(id_plato), pos, clean),
                )


class PlatosRestriccionesDieteticasRepository(PostgresRepository):
    table = "public.platos_restricciones_dieteticas"
    columns = frozenset({"id_plato", "posicion", "restriccion"})

    @classmethod
    def list_for(cls, id_plato: int) -> list[str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT restriccion FROM {cls.table} "
                f"WHERE id_plato=%s ORDER BY posicion",
                (int(id_plato),),
            )
            return [row["restriccion"] for row in cur.fetchall()]

    @classmethod
    def replace_for(cls, id_plato: int, restricciones: list[str]) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_plato=%s",
                (int(id_plato),),
            )
            pos = 0
            for r in restricciones:
                clean = " ".join(str(r).strip().split())[:120]
                if not clean:
                    continue
                pos += 1
                cur.execute(
                    f"INSERT INTO {cls.table} (id_plato, posicion, restriccion) "
                    f"VALUES (%s,%s,%s)",
                    (int(id_plato), pos, clean),
                )


class PlatosInformacionNutricionalRepository(PostgresRepository):
    table = "public.platos_informacion_nutricional"
    columns = frozenset({
        "id_plato", "calorias", "proteinas_g", "carbohidratos_g", "grasas_g",
    })

    @classmethod
    def get_for(cls, id_plato: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_plato=%s",
                (int(id_plato),),
            )
            return cur.fetchone()

    @classmethod
    def upsert_for(
        cls,
        id_plato: int,
        *,
        calorias: float | None = None,
        proteinas_g: float | None = None,
        carbohidratos_g: float | None = None,
        grasas_g: float | None = None,
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.table}
                    (id_plato, calorias, proteinas_g, carbohidratos_g, grasas_g)
                VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT (id_plato) DO UPDATE
                SET calorias=EXCLUDED.calorias,
                    proteinas_g=EXCLUDED.proteinas_g,
                    carbohidratos_g=EXCLUDED.carbohidratos_g,
                    grasas_g=EXCLUDED.grasas_g
                RETURNING *
                """,
                (int(id_plato), calorias, proteinas_g, carbohidratos_g, grasas_g),
            )
            return cur.fetchone()