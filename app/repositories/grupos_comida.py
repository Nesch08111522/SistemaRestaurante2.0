# app/repositories/grupos_comida.py
"""
Repositorio de grupos de comida y sus 4 tablas hijas.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class GruposComidaRepository(PostgresRepository):
    table = "public.grupos_comida"
    columns = frozenset({"id_grupo", "id_anfitrion", "titulo", "invitacion", "vence_en"})

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_grupo=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def get_by_invitacion(cls, invitacion: str) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE invitacion=%s",
                (invitacion.strip()[:120],),
            )
            return cur.fetchone()

    @classmethod
    def insert(
        cls,
        *,
        id_anfitrion: int,
        titulo: str,
        invitacion: str,
        vence_en: datetime | None = None,
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(id_anfitrion, titulo, invitacion, vence_en) "
                "VALUES (%s,%s,%s,%s) RETURNING *",
                (
                    int(id_anfitrion), titulo.strip()[:180],
                    invitacion.strip()[:120], vence_en,
                ),
            )
            return cur.fetchone()


class GruposComidaMiembrosRepository(PostgresRepository):
    table = "public.grupos_comida_miembros"
    columns = frozenset({"id_grupo", "id_usuario", "es_anfitrion"})

    @classmethod
    def list_for(cls, id_grupo: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_grupo=%s",
                (int(id_grupo),),
            )
            return list(cur.fetchall())

    @classmethod
    def add(
        cls, id_grupo: int, id_usuario: int, *, es_anfitrion: bool = False
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} (id_grupo, id_usuario, es_anfitrion) "
                f"VALUES (%s,%s,%s) "
                f"ON CONFLICT (id_grupo, id_usuario) DO UPDATE "
                f"SET es_anfitrion=EXCLUDED.es_anfitrion RETURNING *",
                (int(id_grupo), int(id_usuario), bool(es_anfitrion)),
            )
            return cur.fetchone()


class GruposComidaPreferenciasRepository(PostgresRepository):
    table = "public.grupos_comida_preferencias"
    columns = frozenset({"id_grupo", "id_usuario", "presupuesto"})

    @classmethod
    def get_for(
        cls, id_grupo: int, id_usuario: int
    ) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_grupo=%s AND id_usuario=%s",
                (int(id_grupo), int(id_usuario)),
            )
            return cur.fetchone()

    @classmethod
    def upsert(
        cls, id_grupo: int, id_usuario: int, presupuesto: float | None = None
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} (id_grupo, id_usuario, presupuesto) "
                f"VALUES (%s,%s,%s) "
                f"ON CONFLICT (id_grupo, id_usuario) DO UPDATE "
                f"SET presupuesto=EXCLUDED.presupuesto RETURNING *",
                (int(id_grupo), int(id_usuario), presupuesto),
            )
            return cur.fetchone()


class GruposComidaPreferenciasEvitarRepository(PostgresRepository):
    table = "public.grupos_comida_preferencias_evitar"
    columns = frozenset({"id_grupo", "id_usuario", "alimento"})

    @classmethod
    def list_for(cls, id_grupo: int, id_usuario: int) -> list[str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT alimento FROM {cls.table} "
                f"WHERE id_grupo=%s AND id_usuario=%s ORDER BY alimento",
                (int(id_grupo), int(id_usuario)),
            )
            return [row["alimento"] for row in cur.fetchall()]

    @classmethod
    def replace_for(
        cls, id_grupo: int, id_usuario: int, alimentos: list[str]
    ) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_grupo=%s AND id_usuario=%s",
                (int(id_grupo), int(id_usuario)),
            )
            for a in alimentos:
                clean = " ".join(str(a).strip().split())[:120]
                if not clean:
                    continue
                cur.execute(
                    f"INSERT INTO {cls.table} (id_grupo, id_usuario, alimento) "
                    f"VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
                    (int(id_grupo), int(id_usuario), clean),
                )


class GruposComidaVotosRepository(PostgresRepository):
    table = "public.grupos_comida_votos"
    columns = frozenset({
        "id_grupo", "id_usuario", "id_restaurante", "votado_en",
    })

    @classmethod
    def list_for(cls, id_grupo: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_grupo=%s "
                f"ORDER BY votado_en DESC",
                (int(id_grupo),),
            )
            return list(cur.fetchall())

    @classmethod
    def vote(
        cls, id_grupo: int, id_usuario: int, id_restaurante: int
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(id_grupo, id_usuario, id_restaurante, votado_en) "
                "VALUES (%s,%s,%s,%s) "
                "ON CONFLICT (id_grupo, id_usuario, id_restaurante) "
                "DO UPDATE SET votado_en=EXCLUDED.votado_en RETURNING *",
                (
                    int(id_grupo), int(id_usuario), int(id_restaurante),
                    datetime.now(timezone.utc),
                ),
            )
            return cur.fetchone()