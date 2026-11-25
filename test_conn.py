"""Diagnóstico de solo lectura; nunca imprime credenciales ni datos de usuarios."""
from time import perf_counter


def main():
    from app.db.connection import check_connection
    for attempt in range(3):
        started = perf_counter()
        try:
            ok = check_connection()
        except Exception as error:
            print(f"Conexión no disponible: {type(error).__name__}")
            return 1
        print(f"Prueba {attempt + 1}: ok={ok}, {(perf_counter() - started) * 1000:.1f} ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
