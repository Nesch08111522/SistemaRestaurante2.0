# app/repositories/revision_automatica.py
"""
Repositorio de public.restaurante_revision_automatica y sus atributos.
Columnas de restaurante_revision_automatica:
  id_restaurante, ruta, veredicto_ia, confianza, estado_final,
  version_modelo, requiere_revision_humana, puntuacion_comida,
  puntuacion_riesgo, nivel_riesgo, es_contenido_limpio
"""
from __future__ import annotations

from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


_TIPOS_VALOR = frozenset({"texto", "numero", "booleano", "nulo"})


class RestauranteRevisionAutomaticaRepository(PostgresRepository):
    table = "public.restaurante_revision_automatica"
    columns = frozenset({
        "id_restaurante", "ruta", "veredicto_ia", "confianza",
        "estado_final", "version_modelo", "requiere_revision_humana",
        "puntuacion_comida", "puntuacion_riesgo", "nivel_riesgo",
        "es_contenido_limpio",
    })

    @classmethod
    def get_for(cls, id_restaurante: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_restaurante=%s",
                (int(id_restaurante),),
            )
            return cur.fetchone()

    @classmethod
    def upsert_for(
        cls, id_restaurante: int, **fields: Any
    ) -> dict[str, Any]:
        allowed = cls.columns - {"id_restaurante"}
        payload = {k: v for k, v in fields.items() if k in allowed}
        if "confianza" in payload and payload["confianza"] is not None:
            v = float(payload["confianza"])
            if not 0 <= v <= 1:
                raise ValueError("confianza fuera de rango.")
            payload["confianza"] = v
        columns = ["id_restaurante"] + list(payload)
        placeholders = ",".join(["%s"] * len(columns))
        updates = ",".join(f"{k}=EXCLUDED.{k}" for k in payload)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.table} ({','.join(columns)})
                VALUES ({placeholders})
                ON CONFLICT (id_restaurante) DO UPDATE SET {updates}
                RETURNING *
                """,
                (int(id_restaurante), *payload.values()),
            )
            return cur.fetchone()


class RestauranteRevisionAutomaticaAtributosRepository(PostgresRepository):
    table = "public.restaurante_revision_automatica_atributos"
    columns = frozenset({
        "id_restaurante", "ruta", "tipo_valor",
        "valor_texto", "valor_numero", "valor_booleano",
    })

    @classmethod
    def list_for(cls, id_restaurante: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_restaurante=%s ORDER BY ruta",
                (int(id_restaurante),),
            )
            return list(cur.fetchall())

    @classmethod
    def replace_for(
        cls, id_restaurante: int, atributos: list[dict[str, Any]]
    ) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_restaurante=%s",
                (int(id_restaurante),),
            )
            for attr in atributos:
                ruta = str(attr.get("ruta") or "").strip()
                tipo = str(attr.get("tipo_valor") or "").strip().lower()
                if not ruta or tipo not in _TIPOS_VALOR:
                    continue
                cur.execute(
                    f"INSERT INTO {cls.table} "
                    "(id_restaurante, ruta, tipo_valor, "
                    " valor_texto, valor_numero, valor_booleano) "
                    "VALUES (%s,%s,%s,%s,%s,%s)",
                    (
                        int(id_restaurante), ruta, tipo,
                        attr.get("valor_texto") if tipo == "texto" else None,
                        attr.get("valor_numero") if tipo == "numero" else None,
                        attr.get("valor_booleano") if tipo == "booleano" else None,
                    ),
                )