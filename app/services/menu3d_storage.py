"""Private Supabase Storage gateway; references, never credentials, leave server."""
import os
import re
from urllib.parse import urlsplit
import requests


class IntegrationError(RuntimeError):
    pass


class Storage:
    bucket = 'platos-media'

    def __init__(self):
        self.base = os.getenv('SUPABASE_URL', '').rstrip('/')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
        parsed = urlsplit(self.base)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.path or not key:
            raise IntegrationError('Configura SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY en el servidor.')
        self.headers = {'Authorization': f'Bearer {key}', 'apikey': key}

    def _path(self, path):
        if not re.fullmatch(r'empresas/\d+/restaurantes/\d+/platos/\d+/(originales|procesadas|modelos-3d)/[a-zA-Z0-9_.-]+', path):
            raise ValueError('Ruta de recurso inválida.')
        return f'{self.bucket}/{path}'

    def _request(self, method, endpoint, **kwargs):
        try:
            response = requests.request(method, self.base + '/storage/v1' + endpoint,
                headers={**self.headers, **kwargs.pop('headers', {})}, timeout=(5, 45),
                allow_redirects=False, **kwargs)
            if not 200 <= response.status_code < 300:
                raise IntegrationError('Storage no pudo completar la operación.')
            return response
        except requests.RequestException:
            raise IntegrationError('Storage no está disponible temporalmente.') from None

    def upload(self, path, data, mime):
        self._request('POST', '/object/' + self._path(path), data=data,
            headers={'Content-Type': mime, 'x-upsert': 'true', 'Cache-Control': 'private, max-age=60'})

    def sign(self, path, seconds=120):
        response = self._request('POST', '/object/sign/' + self._path(path), json={'expiresIn': seconds})
        try:
            signed = response.json()['signedURL']
            if not signed.startswith('/object/sign/'):
                raise ValueError()
            return self.base + '/storage/v1' + signed
        except (KeyError, TypeError, ValueError):
            raise IntegrationError('Storage devolvió una referencia inválida.') from None

    def delete(self, paths):
        for path in paths: self._path(path)
        self._request('DELETE', '/object/' + self.bucket, json={'prefixes': paths})
