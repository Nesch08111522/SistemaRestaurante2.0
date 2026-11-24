# app/core/json_encoder.py
"""JSON encoder que serializa datetime/date/time/Decimal en formato ISO 8601."""
from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal

from flask.json.provider import DefaultJSONProvider


class SmartRestoJSONProvider(DefaultJSONProvider):
    """Extiende el provider por defecto para serializar tipos de PostgreSQL."""

    @staticmethod
    def default(o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, date):
            return o.isoformat()
        if isinstance(o, time):
            return o.isoformat()  # "12:00:00"
        if isinstance(o, Decimal):
            return float(o)
        # memoryview (bytea) por si algún día leemos imágenes blob
        if isinstance(o, (bytes, bytearray, memoryview)):
            import base64
            return base64.b64encode(bytes(o)).decode("ascii")
        return DefaultJSONProvider.default(o)