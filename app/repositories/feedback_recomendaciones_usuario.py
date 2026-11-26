"""Private, user-scoped recommendation feedback in PostgreSQL."""
from __future__ import annotations

from typing import Any

from app.db.repository import shared_transaction


class FeedbackRecomendacionesUsuarioRepository:
    table = "public.feedback_recomendaciones_usuario"
    _VALUES = frozenset({"me_interesa", "no_me_interesa"})

    @classmethod
    def list_for_user(cls, id_usuario: int) -> dict[int, str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT id_plato, valor FROM {cls.table} WHERE id_usuario=%s",
                (int(id_usuario),),
            )
            return {int(row["id_plato"]): row["valor"] for row in cur.fetchall()}

    @classmethod
    def upsert(cls, *, id_usuario: int, id_plato: int, valor: str) -> dict[str, Any]:
        if valor not in cls._VALUES:
            raise ValueError("Valor de feedback inválido.")
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""INSERT INTO {cls.table} (id_usuario, id_plato, valor)
                    VALUES (%s,%s,%s)
                    ON CONFLICT (id_usuario, id_plato) DO UPDATE
                    SET valor=EXCLUDED.valor, actualizado_en=CURRENT_TIMESTAMP
                    RETURNING *""",
                (int(id_usuario), int(id_plato), valor),
            )
            return cur.fetchone()
