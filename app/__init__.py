# app/__init__.py
import logging
import uuid
from time import perf_counter

from flask import Flask, g, jsonify, render_template, request
from flask_wtf.csrf import CSRFError
from werkzeug.middleware.proxy_fix import ProxyFix

from app.config import Config
from app.extensions import csrf

logger = logging.getLogger(__name__)


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    app.json.ensure_ascii = False

    from app.core.json_encoder import SmartRestoJSONProvider
    app.json = SmartRestoJSONProvider(app)

    # 1. Validar configuración
    if not app.config.get("TESTING", False):
        Config.validate(app.config)
        logger.info("Configuración validada. Entorno: %s", app.config.get("APP_ENV"))

    # 2. ProxyFix
    trusted_proxy_count = app.config.get("TRUSTED_PROXY_COUNT", 0)
    if trusted_proxy_count:
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=trusted_proxy_count,
            x_proto=trusted_proxy_count,
            x_host=trusted_proxy_count,
        )

    # 3. Verificar conexión y esquema
    if not app.config.get("TESTING", False):
        from app.db.connection import check_application_schema
        check_application_schema()
        logger.info("Esquema PostgreSQL verificado.")

    # Bound multipart size before Flask-WTF reads the body for CSRF validation.
    @app.before_request
    def menu3d_upload_limit():
        if request.endpoint == "ar.upload":
            request.max_content_length = 9 * 1024 * 1024

    # 4. CSRF
    csrf.init_app(app)

    # 5. Metadatos por request
    @app.before_request
    def assign_request_metadata():
        request.performance_start = perf_counter()
        request.request_id = str(uuid.uuid4())

    # 6. Health check
    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok", "service": "smartresto"}), 200

    @app.get("/ready")
    def readiness_check():
        from app.db.connection import check_connection
        try:
            ready = check_connection()
        except Exception:
            ready = False
        return jsonify({"status": "ready" if ready else "unavailable"}), 200 if ready else 503

    @app.after_request
    def record_response(response):
        elapsed = (perf_counter() - getattr(request, "performance_start", perf_counter())) * 1000
        response.headers["Server-Timing"] = f"app;dur={elapsed:.1f}"
        response.headers["X-Request-ID"] = getattr(request, "request_id", "")
        if request.endpoint != "static":
            # HTML contains CSRF/session data; never share-cache it.
            response.headers["Cache-Control"] = "no-store"
        if response.status_code == 503:
            response.headers["Retry-After"] = "30"
        if request.endpoint != "static":
            identity = getattr(g, "session_identity", None) or {}
            logging.getLogger("smartresto.access").info(
                "request_id=%s endpoint=%s method=%s status=%s actor=%s elapsed_ms=%.1f",
                getattr(request, "request_id", ""), request.endpoint,
                request.method, response.status_code, identity.get("id"), elapsed,
            )
        return response

    # 7. Context processor GLOBAL (website, categories, editorial_images, etc.)
    @app.context_processor
    def inject_globals():
        from app.core.context import get_global_context
        return get_global_context(app)

    # 8. Context processor por rol (nav_role, current_user)
    from app.core.context import register_context
    register_context(app)

    # 9. Manejo CSRF
    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        if request.is_json or "/api/" in request.path:
            return jsonify({
                "success": False,
                "error": "Solicitud no autorizada. Verifica el token CSRF.",
                "code": "csrf_invalid",
            }), 400
        return render_template("500.html", status=400), 400

    # 10. Manejo de errores BD
    from app.db.connection import (
        DatabaseConfigurationError,
        DatabaseConnectionError,
    )
    import psycopg

    @app.errorhandler(DatabaseConfigurationError)
    @app.errorhandler(DatabaseConnectionError)
    @app.errorhandler(psycopg.OperationalError)
    def database_unavailable(error):
        g.database_unavailable = True
        logger.error(
            "Base de datos no disponible. request_id=%s",
            getattr(request, "request_id", "unknown"),
        )
        if request.is_json or "/api/" in request.path:
            return jsonify({
                "success": False,
                "error": "El servicio de datos no está disponible temporalmente.",
                "code": "database_unavailable",
                "request_id": getattr(request, "request_id", None),
            }), 503
        return render_template("500.html", status=503), 503

    # 11. Registrar blueprints
    from app.blueprints import register_blueprints
    register_blueprints(app)

    from app.services.menu3d_worker import register_cli
    register_cli(app)

    logger.info("SmartResto inicializado correctamente.")
    return app
