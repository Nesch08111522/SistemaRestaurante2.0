"""In-process review anchor poller, started after a web worker receives traffic."""
import logging
import os
import threading

logger = logging.getLogger(__name__)
_guard = threading.Lock()
_threads = {}


def run_once():
    from app.repositories.anclas_trazabilidad import AnclasTrazabilidadRepository
    from app.services.traceability import _process_onchain
    return _process_onchain(AnclasTrazabilidadRepository, limit=50, tipo_recurso='resena')


def _run(app, interval):
    while True:
        try:
            with app.app_context():
                run_once()
        except Exception as exc:
            # Never log an RPC URL or private key from provider exceptions.
            logger.warning('Procesamiento automático de anclas falló: %s', type(exc).__name__)
        threading.Event().wait(interval)


def ensure_started(app):
    if app.testing or os.getenv('ANCHOR_MODE', 'off').strip().lower() != 'onchain':
        return False
    raw = os.getenv('ANCHOR_AUTO_ENABLED', 'true').strip().lower()
    if raw not in {'1', 'true', 'yes', 'on'}:
        return False
    try:
        interval = max(10, min(int(os.getenv('ANCHOR_AUTO_INTERVAL_SECONDS', '20')), 3600))
    except ValueError:
        logger.error('ANCHOR_AUTO_INTERVAL_SECONDS debe ser un entero.')
        return False
    key = (os.getpid(), id(app))
    with _guard:
        existing = _threads.get(key)
        if existing and existing.is_alive():
            return False
        worker = threading.Thread(target=_run, args=(app, interval), name='review-anchor-worker', daemon=True)
        _threads[key] = worker
        worker.start()
    return True


def register(app):
    @app.before_request
    def start_review_anchor_worker():
        ensure_started(app)
