"""Meshy adapter. Contract verified against official Image/Multi Image to 3D docs.

POST is deliberately never retried automatically: an ambiguous response may
already have incurred a charge. GET failures can be retried by the durable worker.
"""
import os
import re
import time
from typing import Protocol
from urllib.parse import urlsplit
import requests
from app.services.menu3d_storage import IntegrationError
from app.services.menu3d_validation import MAX_GLB


class ImageTo3DProvider(Protocol):
    def submit(self, urls: list[str]) -> str: ...
    def status(self, task_id: str, count: int) -> dict: ...
    def download(self, url: str) -> tuple[bytes, str]: ...


class MeshyProvider:
    base = 'https://api.meshy.ai/openapi/v1/'

    def __init__(self):
        key = os.getenv('MESHY_API_KEY', '')
        if not key:
            raise IntegrationError('Configura MESHY_API_KEY para habilitar la generación.')
        self.headers = {'Authorization': f'Bearer {key}'}

    @staticmethod
    def endpoint(count):
        return 'image-to-3d' if count == 1 else 'multi-image-to-3d'

    def submit(self, urls):
        if not 1 <= len(urls) <= 4:
            raise ValueError('Se requieren entre una y cuatro fotografías.')
        payload = {'image_url': urls[0]} if len(urls) == 1 else {'image_urls': urls}
        payload.update(ai_model=os.getenv('MESHY_MODEL', 'meshy-7.1'),
                       should_texture=True, target_formats=['glb'])
        try:
            r = requests.post(self.base + self.endpoint(len(urls)), headers=self.headers,
                              json=payload, timeout=(5, 45), allow_redirects=False)
            r.raise_for_status()
            task = r.json()['result']
            if not isinstance(task, str) or not re.fullmatch(r'[a-zA-Z0-9-]{1,100}', task):
                raise ValueError()
            return task
        except (requests.RequestException, KeyError, ValueError, TypeError):
            raise IntegrationError('No se confirmó el envío. Revisa la tarea en Meshy antes de volver a generar.') from None

    def status(self, task_id, count):
        if not re.fullmatch(r'[a-zA-Z0-9-]{1,100}', task_id):
            raise ValueError('Identificador externo inválido.')
        try:
            r = requests.get(self.base + self.endpoint(count) + '/' + task_id,
                             headers=self.headers, timeout=(5, 30), allow_redirects=False)
            r.raise_for_status()
            task = r.json()
            if task.get('status') not in {'PENDING','IN_PROGRESS','SUCCEEDED','FAILED','CANCELED'}:
                raise ValueError()
            return task
        except (requests.RequestException, ValueError, AttributeError):
            raise IntegrationError('No se pudo consultar el progreso del proveedor.') from None

    def download(self, url):
        parsed = urlsplit(url)
        hosts = {h.strip().lower() for h in os.getenv('MENU3D_ASSET_HOSTS', 'assets.meshy.ai').split(',') if h.strip()}
        if parsed.scheme != 'https' or parsed.hostname not in hosts or parsed.username or parsed.password or parsed.port not in (None,443):
            raise ValueError('El origen del modelo no está autorizado.')
        # No auth headers, redirects or user supplied URLs. Exact trusted CDN allowlist.
        try:
            with requests.get(url, stream=True, timeout=(5, 30), allow_redirects=False) as r:
                if r.status_code != 200:
                    raise IntegrationError('No se pudo descargar el modelo generado.')
                if int(r.headers.get('Content-Length', 0)) > MAX_GLB:
                    raise ValueError('El modelo supera los 50 MB.')
                data = bytearray()
                started = time.monotonic()
                for chunk in r.iter_content(65536):
                    data.extend(chunk)
                    if len(data) > MAX_GLB or time.monotonic() - started > 120:
                        raise ValueError('El modelo supera el límite de tamaño o descarga.')
                return bytes(data), r.headers.get('Content-Type', '')
        except requests.RequestException:
            raise IntegrationError('Descarga interrumpida; se reintentará sin crear otra tarea.') from None


def provider():
    if os.getenv('MENU3D_PROVIDER', 'meshy') != 'meshy':
        raise IntegrationError('Proveedor 3D no configurado o no compatible.')
    return MeshyProvider()
