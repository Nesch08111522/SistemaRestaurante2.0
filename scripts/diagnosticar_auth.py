"""Read-only account diagnostics. Never outputs passwords or hashes."""
import sys
import json
from app.repositories.usuarios import UsuariosRepository
from app.models.user import UserModel


def main():
    identifier = sys.argv[1] if len(sys.argv) > 1 else "admin"
    try:
        row = UsuariosRepository.get_by_login(identifier)
    except Exception as error:
        print("CONEXION_NO_DISPONIBLE:", type(error).__name__)
        return 1
    if not row:
        print("CUENTA_NO_ENCONTRADA_O_CORREO_AMBIGUO")
        return 1
    print("CUENTA_ENCONTRADA")
    print("ESTADO:", "ACTIVE" if UserModel.is_active(row) else "NO_ACTIVA_O_SIN_ESTADO")
    raw_status = row.get("estado_cuenta")
    print("ESTADO_GUARDADO:", json.dumps(raw_status, ensure_ascii=True, default=str))
    print("ACTIVACION_PENDIENTE:", json.dumps(row.get("activacion_pendiente"), default=str))
    stored = row.get("hash_contrasena") or ""
    family = next((name for prefix, name in [("scrypt:", "scrypt"), ("pbkdf2:", "pbkdf2"), ("$2a$", "bcrypt"), ("$2b$", "bcrypt"), ("$2y$", "bcrypt"), ("$argon2", "argon2")] if stored.startswith(prefix)), "VACIO" if not stored else "DESCONOCIDO")
    print("FORMATO_PASSWORD:", family)
    print("No se verifico la contrasena; no se modifico la cuenta.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
