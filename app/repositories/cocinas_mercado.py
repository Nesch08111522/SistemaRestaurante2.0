# app/repositories/cocinas_mercado.py
"""
Repositorio de cocinas de mercado y sus 5 tablas hijas.
"""
from __future__ import annotations

from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class CocinasMercadoRepository(PostgresRepository):
    table = "public.cocinas_mercado"
    columns = frozenset({
        "id_cocina", "codigo_pin", "tipo", "id_lider",
        "capacidad_asientos", "direccion_recojo", "radio",
        "recompensa", "puntos_fidelidad", "capacidad",
        "nombres_equipo", "minutos_mesa",
    })

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_cocina=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def list_all(cls) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {cls.table} ORDER BY id_cocina")
            return list(cur.fetchall())

    @classmethod
    def insert(
        cls,
        *,
        tipo: str,
        id_lider: int | None = None,
        capacidad_asientos: int | None = None,
        direccion_recojo: str | None = None,
        radio: int | None = None,
        recompensa: float | None = None,
        puntos_fidelidad: int | None = None,
        capacidad: int | None = None,
        nombres_equipo: str | None = None,
        minutos_mesa: int | None = None,
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(tipo, id_lider, capacidad_asientos, direccion_recojo, "
                " radio, recompensa, puntos_fidelidad, capacidad, "
                " nombres_equipo, minutos_mesa) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *",
                (
                    tipo.strip()[:80], id_lider, capacidad_asientos,
                    direccion_recojo, radio, recompensa, puntos_fidelidad,
                    capacidad, nombres_equipo, minutos_mesa,
                ),
            )
            return cur.fetchone()


class CocinasMercadoEquipoRepository(PostgresRepository):
    table = "public.cocinas_mercado_equipo"
    columns = frozenset({"id_cocina", "posicion", "id_usuario"})

    @classmethod
    def list_for(cls, id_cocina: int) -> list[int]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT id_usuario FROM {cls.table} "
                f"WHERE id_cocina=%s ORDER BY posicion",
                (int(id_cocina),),
            )
            return [row["id_usuario"] for row in cur.fetchall()]

    @classmethod
    def replace_for(cls, id_cocina: int, ids_usuarios: list[int]) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_cocina=%s",
                (int(id_cocina),),
            )
            pos = 0
            vistos = set()
            for uid in ids_usuarios:
                uid = int(uid)
                if uid in vistos:
                    continue
                vistos.add(uid)
                pos += 1
                cur.execute(
                    f"INSERT INTO {cls.table} (id_cocina, posicion, id_usuario) "
                    f"VALUES (%s,%s,%s)",
                    (int(id_cocina), pos, uid),
                )


class CocinasMercadoZonasRepository(PostgresRepository):
    table = "public.cocinas_mercado_zonas"
    columns = frozenset({"id_cocina", "posicion", "zona"})

    @classmethod
    def list_for(cls, id_cocina: int) -> list[str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT zona FROM {cls.table} "
                f"WHERE id_cocina=%s ORDER BY posicion",
                (int(id_cocina),),
            )
            return [row["zona"] for row in cur.fetchall()]

    @classmethod
    def replace_for(cls, id_cocina: int, zonas: list[str]) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_cocina=%s",
                (int(id_cocina),),
            )
            pos = 0
            for z in zonas:
                clean = " ".join(str(z).strip().split())[:120]
                if not clean:
                    continue
                pos += 1
                cur.execute(
                    f"INSERT INTO {cls.table} (id_cocina, posicion, zona) "
                    f"VALUES (%s,%s,%s)",
                    (int(id_cocina), pos, clean),
                )


class CocinasMercadoCanalesRepository(PostgresRepository):
    table = "public.cocinas_mercado_canales"
    columns = frozenset({"id_cocina", "posicion", "canal"})

    @classmethod
    def list_for(cls, id_cocina: int) -> list[str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT canal FROM {cls.table} "
                f"WHERE id_cocina=%s ORDER BY posicion",
                (int(id_cocina),),
            )
            return [row["canal"] for row in cur.fetchall()]

    @classmethod
    def replace_for(cls, id_cocina: int, canales: list[str]) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_cocina=%s",
                (int(id_cocina),),
            )
            pos = 0
            for c in canales:
                clean = " ".join(str(c).strip().split())[:80]
                if not clean:
                    continue
                pos += 1
                cur.execute(
                    f"INSERT INTO {cls.table} (id_cocina, posicion, canal) "
                    f"VALUES (%s,%s,%s)",
                    (int(id_cocina), pos, clean),
                )


class CocinasMercadoDespensaRepository(PostgresRepository):
    table = "public.cocinas_mercado_despensa"
    columns = frozenset({
        "id_insumo", "id_cocina", "nombre_insumo", "cantidad",
        "unidad", "notas",
    })

    @classmethod
    def list_for(cls, id_cocina: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_cocina=%s "
                f"ORDER BY nombre_insumo",
                (int(id_cocina),),
            )
            return list(cur.fetchall())

    @classmethod
    def insert(
        cls,
        *,
        id_cocina: int,
        nombre_insumo: str,
        cantidad: float | None = None,
        unidad: str | None = None,
        notas: str | None = None,
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(id_cocina, nombre_insumo, cantidad, unidad, notas) "
                "VALUES (%s,%s,%s,%s,%s) RETURNING *",
                (
                    int(id_cocina), nombre_insumo.strip()[:160],
                    cantidad, unidad, notas,
                ),
            )
            return cur.fetchone()