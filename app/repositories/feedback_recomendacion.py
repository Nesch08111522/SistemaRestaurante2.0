# app/repositories/feedback_recomendacion.py
"""
Repositorio de public.feedback_recomendacion y sus 4 tablas hijas.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class FeedbackRecomendacionRepository(PostgresRepository):
    table = "public.feedback_recomendacion"
    columns = frozenset({"id_feedback"})

    @classmethod
    def create_empty(cls) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} DEFAULT VALUES RETURNING *"
            )
            return cur.fetchone()


class FeedbackRecomendacionItemsRepository(PostgresRepository):
    table = "public.feedback_recomendacion_items"
    columns = frozenset({
        "id_feedback", "entidad_clave", "tipo_entidad",
        "id_entidad", "interaccion",
    })

    @classmethod
    def list_for(cls, id_feedback: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_feedback=%s "
                f"ORDER BY entidad_clave",
                (int(id_feedback),),
            )
            return list(cur.fetchall())

    @classmethod
    def upsert(
        cls,
        *,
        id_feedback: int,
        entidad_clave: str,
        interaccion: str,
        tipo_entidad: str | None = None,
        id_entidad: int | None = None,
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.table}
                    (id_feedback, entidad_clave, tipo_entidad, id_entidad, interaccion)
                VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT (id_feedback, entidad_clave) DO UPDATE
                SET tipo_entidad=EXCLUDED.tipo_entidad,
                    id_entidad=EXCLUDED.id_entidad,
                    interaccion=EXCLUDED.interaccion
                RETURNING *
                """,
                (
                    int(id_feedback), entidad_clave.strip()[:160],
                    tipo_entidad, id_entidad, interaccion.strip()[:80],
                ),
            )
            return cur.fetchone()


class FeedbackRecomendacionRecientesRepository(PostgresRepository):
    table = "public.feedback_recomendacion_recientes"
    columns = frozenset({"id_feedback", "posicion", "entidad_clave"})

    @classmethod
    def list_for(cls, id_feedback: int) -> list[str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT entidad_clave FROM {cls.table} "
                f"WHERE id_feedback=%s ORDER BY posicion",
                (int(id_feedback),),
            )
            return [row["entidad_clave"] for row in cur.fetchall()]

    @classmethod
    def replace_for(cls, id_feedback: int, entidades: list[str]) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_feedback=%s",
                (int(id_feedback),),
            )
            pos = 0
            vistos = set()
            for entidad in entidades:
                clean = " ".join(str(entidad).strip().split())[:160]
                if not clean or clean in vistos:
                    continue
                vistos.add(clean)
                pos += 1
                cur.execute(
                    f"INSERT INTO {cls.table} (id_feedback, posicion, entidad_clave) "
                    f"VALUES (%s,%s,%s)",
                    (int(id_feedback), pos, clean),
                )


class FeedbackRecomendacionSenalesRepository(PostgresRepository):
    table = "public.feedback_recomendacion_senales"
    columns = frozenset({
        "id_feedback", "entidad_clave", "vistas",
        "ultima_vista", "actualizado_en",
    })

    @classmethod
    def list_for(cls, id_feedback: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_feedback=%s "
                f"ORDER BY vistas DESC",
                (int(id_feedback),),
            )
            return list(cur.fetchall())

    @classmethod
    def record_view(
        cls, *, id_feedback: int, entidad_clave: str
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.table}
                    (id_feedback, entidad_clave, vistas, ultima_vista, actualizado_en)
                VALUES (%s,%s,1,%s,%s)
                ON CONFLICT (id_feedback, entidad_clave) DO UPDATE
                SET vistas = {cls.table}.vistas + 1,
                    ultima_vista = EXCLUDED.ultima_vista,
                    actualizado_en = EXCLUDED.actualizado_en
                RETURNING *
                """,
                (int(id_feedback), entidad_clave.strip()[:160], now, now),
            )
            return cur.fetchone()