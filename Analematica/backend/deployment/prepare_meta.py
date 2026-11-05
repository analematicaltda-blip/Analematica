"""Resolve Meta return URL from this deployment, without tokens or network calls."""
import argparse
import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit


def resolve_origin(origin=None, environ=None, port=8090):
    env = os.environ if environ is None else environ
    origin = origin or env.get('ANALEMATICA_PUBLIC_ORIGIN')
    if not origin:
        name = env.get('CODESPACE_NAME', '')
        domain = env.get('GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN', 'app.github.dev')
        if re.fullmatch(r'[a-z0-9-]+', name) and domain == 'app.github.dev':
            origin = f'https://{name}-{port}.{domain}'
    if not origin:
        raise ValueError('Este entorno no declara una URL pública. Ejecuta este script dentro del Codespace que sirve Analemática o configura ANALEMATICA_PUBLIC_ORIGIN.')
    p = urlsplit(origin)
    if p.scheme != 'https' or not p.hostname or p.username or p.password or p.query or p.fragment or p.path not in ['', '/']:
        raise ValueError('El origen debe ser HTTPS, sin rutas, credenciales ni parámetros.')
    p.port  # Reject malformed ports.
    return origin.rstrip('/')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origin')
    parser.add_argument('--port', type=int, default=8090)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error('Puerto no válido.')
    try:
        origin = resolve_origin(args.origin, port=args.port)
    except ValueError as error:
        parser.error(str(error))
    config = json.loads((Path(__file__).parents[2] / 'Frontend/config/meta-public.json').read_text())
    print(json.dumps({**config, 'redirect_uri': origin + config['callback_path'],
                      'instagram_redirect_uri': origin + config['instagram_callback_path'],
                      'webhook_url': origin + '/api/v1/workspace/meta/webhooks/receive',
                      'owner_panel': origin + '/admin.html#tab-meta-ads',
                      'status': 'prepared_not_authorized',
                      'instagram_backend_flow': 'implemented_pending_provider_validation',
                      'note': 'Registra redirect_uri en Meta. No se guardaron secretos ni se cambió ninguna cuenta.'}, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
