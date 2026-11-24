# app/repositories/empresas_suscripciones.py
"""
Repositorio de public.empresas_suscripciones y su tabla hija
public.empresas_suscripcion_modulos_desactivados.

Columnas del .sql:
  empresas_suscripciones: id_empresa, plan, estado, revision,
    inicia_el, vence_el, provisionada_en
  empresas_suscripcion_modulos_desactivados: id_empresa, modulo
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class EmpresasSuscripcionesRepository(PostgresRepository):
    table = "public.empresas_suscripciones"
    columns = frozenset({
        "id_empresa", "plan", "estado", "revision",
        "inicia_el", "vence_el", "provisionada_en",
    })

    PLANES = ("basic", "decente", "premium")
    ESTADOS = ("active", "suspended")

    @classmethod
    def get_by_empresa(cls, id_empresa: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_empresa=%s",
                (int(id_empresa),),
            )
            return cur.fetchone()

    @classmethod
    def upsert_for_empresa(
        cls,
        id_empresa: int,
        *,
        plan: str,
        estado: str = "active",
        inicia_el: date | None = None,
        vence_el: date | None = None,
        revision: int = 1,
    ) -> dict[str, Any]:
        if plan not in cls.PLANES:
            raise ValueError(f"Plan inválido: {plan}")
        if estado not in cls.ESTADOS:
            raise ValueError(f"Estado inválido: {estado}")
        now = datetime.now(timezone.utc)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.table}
                    (id_empresa, plan, estado, revision, inicia_el, vence_el, provisionada_en)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id_empresa) DO UPDATE
                SET plan=EXCLUDED.plan,
                    estado=EXCLUDED.estado,
                    revision=EXCLUDED.revision,
                    inicia_el=EXCLUDED.inicia_el,
                    vence_el=EXCLUDED.vence_el,
                    provisionada_en=EXCLUDED.provisionada_en
                RETURNING *
                """,
                (int(id_empresa), plan, estado, int(revision), inicia_el, vence_el, now),
            )
            return cur.fetchone()

    @classmethod
    def set_disabled_modules(cls, id_empresa: int, modulos: list[str]) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                "DELETE FROM public.empresas_suscripcion_modulos_desactivados "
                "WHERE id_empresa=%s",
                (int(id_empresa),),
            )
            for modulo in modulos:
                clean = str(modulo).strip().lower()[:100]
                if not clean:
                    continue
                cur.execute(
                    "INSERT INTO public.empresas_suscripcion_modulos_desactivados "
                    "(id_empresa, modulo) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                    (int(id_empresa), clean),
                )

    @classmethod
    def get_disabled_modules(cls, id_empresa: int) -> list[str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT modulo FROM public.empresas_suscripcion_modulos_desactivados "
                "WHERE id_empresa=%s ORDER BY modulo",
                (int(id_empresa),),
            )
            return [row["modulo"] for row in cur.fetchall()]