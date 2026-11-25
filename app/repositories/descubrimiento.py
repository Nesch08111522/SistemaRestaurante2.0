# app/repositories/descubrimiento.py
"""
Repositorio de public.fuentes_descubrimiento y ejecuciones_descubrimiento.
Columnas de fuentes_descubrimiento:
  id_fuente, nombre, tipo, url, usa_ia, habilitada, radio_km,
  dias_actualizacion, ultimo_error, creada_en,
  inicio_ultima_consulta, proxima_consulta
Columnas de ejecuciones_descubrimiento:
  id_ejecucion, id_fuente, id_usuario_actor, nombre_fuente_snapshot,
  estado, tipo_error, mensaje_error, iniciada_en, finalizada_en
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.db.repository import PostgresRepository, shared_transaction


class FuentesDescubrimientoRepository(PostgresRepository):
    table = "public.fuentes_descubrimiento"
    columns = frozenset({
        "id_fuente", "nombre", "tipo", "url", "usa_ia",
        "habilitada", "radio_km", "dias_actualizacion", "ultimo_error",
        "creada_en", "inicio_ultima_consulta", "proxima_consulta",
    })

    @classmethod
    def get_by_id(cls, item_id: int) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_fuente=%s",
                (int(item_id),),
            )
            return cur.fetchone()

    @classmethod
    def list_enabled(cls) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE habilitada=TRUE "
                f"ORDER BY id_fuente",
            )
            return list(cur.fetchall())

    @classmethod
    def list_due(cls, *, limit: int = 50) -> list[dict[str, Any]]:
        """Fuentes con `proxima_consulta` vencida o nula, listas para consultar."""
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} "
                f"WHERE habilitada=TRUE "
                f"  AND (proxima_consulta IS NULL OR proxima_consulta <= now()) "
                f"ORDER BY proxima_consulta NULLS FIRST "
                f"LIMIT %s",
                (int(limit),),
            )
            return list(cur.fetchall())

    @classmethod
    def insert(
        cls,
        *,
        nombre: str,
        tipo: str,
        url: str,
        usa_ia: bool = False,
        radio_km: float | None = None,
        dias_actualizacion: int | None = None,
    ) -> dict[str, Any]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(nombre, tipo, url, usa_ia, habilitada, radio_km, "
                " dias_actualizacion, creada_en) "
                "VALUES (%s,%s,%s,%s,TRUE,%s,%s,%s) RETURNING *",
                (
                    nombre.strip()[:180], tipo.strip()[:40], url,
                    bool(usa_ia), radio_km, dias_actualizacion,
                    datetime.now(timezone.utc),
                ),
            )
            return cur.fetchone()

    @classmethod
    def mark_run(
        cls, id_fuente: int, *, error: str | None = None
    ) -> dict[str, Any] | None:
        now = datetime.now(timezone.utc)
        proxima = None
        if error is None:
            # Recalcular próxima consulta según dias_actualizacion
            with shared_transaction() as conn, conn.cursor() as cur:
                cur.execute(
                    f"SELECT dias_actualizacion FROM {cls.table} WHERE id_fuente=%s",
                    (int(id_fuente),),
                )
                row = cur.fetchone()
                if row and row["dias_actualizacion"]:
                    from datetime import timedelta
                    proxima = now + timedelta(days=int(row["dias_actualizacion"]))
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} "
                f"SET inicio_ultima_consulta=%s, ultimo_error=%s, proxima_consulta=%s "
                f"WHERE id_fuente=%s RETURNING *",
                (now, error, proxima, int(id_fuente)),
            )
            return cur.fetchone()


class EjecucionesDescubrimientoRepository(PostgresRepository):
    table = "public.ejecuciones_descubrimiento"
    columns = frozenset({
        "id_ejecucion", "id_fuente", "id_usuario_actor",
        "nombre_fuente_snapshot", "estado", "tipo_error",
        "mensaje_error", "iniciada_en", "finalizada_en",
    })

    @classmethod
    def list_by_fuente(
        cls, id_fuente: int, *, limit: int = 50
    ) -> list[dict[str, Any]]:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {cls.table} WHERE id_fuente=%s "
                f"ORDER BY iniciada_en DESC NULLS LAST LIMIT %s",
                (int(id_fuente), int(limit)),
            )
            return list(cur.fetchall())

    @classmethod
    def start(
        cls,
        *,
        id_fuente: int,
        nombre_fuente_snapshot: str,
        id_usuario_actor: int | None = None,
        estado: str = "running",
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"INSERT INTO {cls.table} "
                "(id_fuente, id_usuario_actor, nombre_fuente_snapshot, "
                " estado, iniciada_en) "
                "VALUES (%s,%s,%s,%s,%s) RETURNING *",
                (
                    int(id_fuente), id_usuario_actor,
                    nombre_fuente_snapshot.strip()[:180],
                    estado.strip()[:40], now,
                ),
            )
            return cur.fetchone()

    @classmethod
    def finish(
        cls,
        id_ejecucion: int,
        *,
        estado: str,
        tipo_error: str | None = None,
        mensaje_error: str | None = None,
    ) -> dict[str, Any] | None:
        with shared_transaction() as conn, conn.cursor() as cur:
            cur.execute(
                f"UPDATE {cls.table} "
                f"SET estado=%s, tipo_error=%s, mensaje_error=%s, finalizada_en=%s "
                f"WHERE id_ejecucion=%s RETURNING *",
                (
                    estado.strip()[:40], tipo_error, mensaje_error,
                    datetime.now(timezone.utc), int(id_ejecucion),
                ),
            )
            return cur.fetchone()