# app/repositories/moderaciones.py
"""
Repositorio de public.moderaciones y sus 5 tablas hijas.
Columnas del .sql (moderaciones):
  id_moderacion, id_usuario, tipo_contenido, id_contenido, estado, motivo,
  marcado, veredicto_ia, confianza_ia, estado_aprobacion, origen_decision,
  reversible, notas_administrador, id_decisor_humano,
  decidido_humanamente_en, id_legado, creado_en, actualizado_en
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


_ORIGENES_ATRIBUTO = frozenset({"texto", "numero", "booleano", "nulo"})


class ModeracionesRepository(PostgresRepository):
    table = "public.moderaciones"
    columns = frozenset({
        "id_moderacion", "id_usuario", "tipo_contenido", "id_contenido",
        "estado", "motivo", "marcado", "veredicto_ia", "confianza_ia",
        "estado_aprobacion", "origen_decision", "reversible",
        "notas_administrador", "id_decisor_humano",
        "decidido_humanamente_en", "id_legado", "creado_en", "actualizado_en",
    })

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_moderacion=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def list_by_estado(
        cls, estado: str, *, limit: int = 100
    ) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE estado=%s "
                f"ORDER BY creado_en DESC NULLS LAST LIMIT %s",
                (estado, int(limit)),
            )
            return list(cur.fetchall())

    @classmethod
    def list_by_contenido(
        cls, tipo_contenido: str, id_contenido: int
    ) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} "
                f"WHERE tipo_contenido=%s AND id_contenido=%s "
                f"ORDER BY creado_en DESC NULLS LAST",
                (tipo_contenido.strip(), int(id_contenido)),
            )
            return list(cur.fetchall())

    @classmethod
    def insert(
        cls,
        *,
        tipo_contenido: str,
        id_contenido: int | None = None,
        id_usuario: int | None = None,
        estado: str | None = None,
        motivo: str | None = None,
        marcado: bool = False,
        veredicto_ia: str | None = None,
        confianza_ia: float | None = None,
        estado_aprobacion: str | None = None,
        origen_decision: str | None = None,
        reversible: bool | None = None,
        notas_administrador: str | None = None,
        id_decisor_humano: int | None = None,
    ) -> dict[str, Any]:
        if confianza_ia is not None and not (0 <= float(confianza_ia) <= 1):
            raise ValueError("confianza_ia debe estar entre 0 y 1.")
        now = datetime.now(timezone.utc)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.table}
                    (id_usuario, tipo_contenido, id_contenido, estado, motivo,
                     marcado, veredicto_ia, confianza_ia, estado_aprobacion,
                     origen_decision, reversible, notas_administrador,
                     id_decisor_humano, decidido_humanamente_en,
                     creado_en, actualizado_en)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING *
                """,
                (
                    id_usuario, tipo_contenido.strip()[:60], id_contenido,
                    estado, motivo, bool(marcado), veredicto_ia,
                    float(confianza_ia) if confianza_ia is not None else None,
                    estado_aprobacion, origen_decision, reversible,
                    notas_administrador,
                    id_decisor_humano,
                    datetime.now(timezone.utc) if id_decisor_humano else None,
                    now, now,
                ),
            )
            return cur.fetchone()

    @classmethod
    def update_fields(cls, id_moderacion: int, values: dict[str, Any]) -> dict[str, Any] | None:
        allowed = cls.columns - {"id_moderacion", "creado_en"}
        payload = {k: v for k, v in values.items() if k in allowed}
        if not payload:
            return cls.get_by_id(id_moderacion)
        payload["actualizado_en"] = datetime.now(timezone.utc)
        names = list(payload)
        assignments = ",".join(f"{name}=%s" for name in names)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} SET {assignments} "
                f"WHERE id_moderacion=%s RETURNING *",
                tuple(payload[name] for name in names) + (int(id_moderacion),),
            )
            return cur.fetchone()


class ModeracionesBanderasRepository(PostgresRepository):
    table = "public.moderaciones_banderas"
    columns = frozenset({"id_moderacion", "posicion", "bandera"})

    @classmethod
    def list_for(cls, id_moderacion: int) -> list[str]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT bandera FROM {cls.table} "
                f"WHERE id_moderacion=%s ORDER BY posicion",
                (int(id_moderacion),),
            )
            return [row["bandera"] for row in cur.fetchall()]

    @classmethod
    def replace_for(cls, id_moderacion: int, banderas: list[str]) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_moderacion=%s",
                (int(id_moderacion),),
            )
            pos = 0
            for bandera in banderas:
                clean = " ".join(str(bandera).strip().split())
                if not clean:
                    continue
                pos += 1
                cur.execute(
                    f"INSERT INTO {cls.table} (id_moderacion, posicion, bandera) "
                    f"VALUES (%s,%s,%s)",
                    (int(id_moderacion), pos, clean),
                )


class ModeracionesHistorialEstadosRepository(PostgresRepository):
    table = "public.moderaciones_historial_estados"
    columns = frozenset({
        "id_moderacion", "posicion", "estado_anterior", "estado_nuevo",
        "origen", "notas", "id_usuario_actor", "ocurrido_en",
    })

    @classmethod
    def list_for(cls, id_moderacion: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} "
                f"WHERE id_moderacion=%s ORDER BY posicion",
                (int(id_moderacion),),
            )
            return list(cur.fetchall())

    @classmethod
    def append(
        cls,
        id_moderacion: int,
        *,
        estado_nuevo: str,
        estado_anterior: str | None = None,
        origen: str | None = None,
        notas: str | None = None,
        id_usuario_actor: int | None = None,
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT COALESCE(MAX(posicion),0)+1 AS next_pos "
                f"FROM {cls.table} WHERE id_moderacion=%s",
                (int(id_moderacion),),
            )
            next_pos = cur.fetchone()["next_pos"]
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(id_moderacion, posicion, estado_anterior, estado_nuevo, "
                " origen, notas, id_usuario_actor, ocurrido_en) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *",
                (
                    int(id_moderacion), int(next_pos), estado_anterior,
                    estado_nuevo.strip()[:80], origen, notas,
                    id_usuario_actor, datetime.now(timezone.utc),
                ),
            )
            return cur.fetchone()


class ModeracionesContenidoAtributosRepository(PostgresRepository):
    table = "public.moderaciones_contenido_atributos"
    columns = frozenset({
        "id_moderacion", "ruta", "tipo_valor",
        "valor_texto", "valor_numero", "valor_booleano",
    })

    @classmethod
    def list_for(cls, id_moderacion: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_moderacion=%s ORDER BY ruta",
                (int(id_moderacion),),
            )
            return list(cur.fetchall())

    @classmethod
    def replace_for(
        cls, id_moderacion: int, atributos: list[dict[str, Any]]
    ) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_moderacion=%s",
                (int(id_moderacion),),
            )
            for attr in atributos:
                ruta = str(attr.get("ruta") or "").strip()
                tipo = str(attr.get("tipo_valor") or "").strip().lower()
                if not ruta or tipo not in _ORIGENES_ATRIBUTO:
                    continue
                cur.execute(
                    f"INSERT INTO {cls.table} "
                    "(id_moderacion, ruta, tipo_valor, "
                    " valor_texto, valor_numero, valor_booleano) "
                    "VALUES (%s,%s,%s,%s,%s,%s)",
                    (
                        int(id_moderacion), ruta, tipo,
                        attr.get("valor_texto") if tipo == "texto" else None,
                        attr.get("valor_numero") if tipo == "numero" else None,
                        attr.get("valor_booleano") if tipo == "booleano" else None,
                    ),
                )


class ModeracionesEvaluacionesIARepository(PostgresRepository):
    table = "public.moderaciones_evaluaciones_ia"
    columns = frozenset({
        "id_moderacion", "ruta", "veredicto_ia", "confianza",
        "tipo_contenido", "estado_final", "version_modelo",
        "requiere_revision_humana", "puntuacion_comida",
        "puntuacion_riesgo", "nivel_riesgo", "es_contenido_limpio",
        "senal_critica", "diccionario_puede_juzgar", "sospecha_evasion",
        "ratio_conocido", "ratio_script", "marcadores_extranjeros",
        "idioma_desconocido",
    })

    @classmethod
    def get_for(cls, id_moderacion: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_moderacion=%s",
                (int(id_moderacion),),
            )
            return cur.fetchone()

    @classmethod
    def upsert_for(
        cls,
        id_moderacion: int,
        **fields: Any,
    ) -> dict[str, Any]:
        allowed = cls.columns - {"id_moderacion"}
        payload = {k: v for k, v in fields.items() if k in allowed}
        if not payload:
            return cls.get_for(id_moderacion) or {"id_moderacion": id_moderacion}
        columns = ["id_moderacion"] + list(payload.keys())
        placeholders = ",".join(["%s"] * len(columns))
        updates = ",".join(f"{k}=EXCLUDED.{k}" for k in payload.keys())
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO {cls.table} ({','.join(columns)})
                VALUES ({placeholders})
                ON CONFLICT (id_moderacion) DO UPDATE SET {updates}
                RETURNING *
                """,
                (int(id_moderacion), *payload.values()),
            )
            return cur.fetchone()


class ModeracionesEvaluacionesIAAtributosRepository(PostgresRepository):
    table = "public.moderaciones_evaluaciones_ia_atributos"
    columns = frozenset({
        "id_moderacion", "ruta", "tipo_valor",
        "valor_texto", "valor_numero", "valor_booleano",
    })

    @classmethod
    def list_for(cls, id_moderacion: int) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_moderacion=%s ORDER BY ruta",
                (int(id_moderacion),),
            )
            return list(cur.fetchall())

    @classmethod
    def replace_for(
        cls, id_moderacion: int, atributos: list[dict[str, Any]]
    ) -> None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {cls.table} WHERE id_moderacion=%s",
                (int(id_moderacion),),
            )
            for attr in atributos:
                ruta = str(attr.get("ruta") or "").strip()
                tipo = str(attr.get("tipo_valor") or "").strip().lower()
                if not ruta or tipo not in _ORIGENES_ATRIBUTO:
                    continue
                cur.execute(
                    f"INSERT INTO {cls.table} "
                    "(id_moderacion, ruta, tipo_valor, "
                    " valor_texto, valor_numero, valor_booleano) "
                    "VALUES (%s,%s,%s,%s,%s,%s)",
                    (
                        int(id_moderacion), ruta, tipo,
                        attr.get("valor_texto") if tipo == "texto" else None,
                        attr.get("valor_numero") if tipo == "numero" else None,
                        attr.get("valor_booleano") if tipo == "booleano" else None,
                    ),
                )