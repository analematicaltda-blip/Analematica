import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
DEPLOY = ROOT / 'BACKEND/deployment'

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class LocalConfigurationTests(unittest.TestCase):
    def test_generated_credentials_are_private_unique_and_not_overwritten(self):
        init = load('init_local', DEPLOY / 'init_local.py')
        with tempfile.TemporaryDirectory() as temp, contextlib.redirect_stdout(io.StringIO()):
            init.initialize(Path(temp))
            before = {p.name: p.read_bytes() for p in Path(temp).iterdir()}
            init.initialize(Path(temp))
            self.assertEqual(before, {p.name: p.read_bytes() for p in Path(temp).iterdir()})
            keys = []
            for name in ['sgacd', 'erp-tur', 'turismo']:
                config = dict(line.split('=', 1) for line in before[name + '.env'].decode().splitlines())
                keys.append(config.get('SECRET_KEY', config.get('DJANGO_SECRET_KEY')))
                self.assertIn('@' + name + '-db:5432/', config['DATABASE_URL'])
            self.assertEqual(len(set(keys)), 3)
            if os.name != 'nt':
                self.assertTrue(all((p.stat().st_mode & 0o077) == 0 for p in Path(temp).iterdir()))

    def test_services_have_independent_configuration_ports_and_no_public_database(self):
        config = json.loads((DEPLOY / 'compose.yaml').read_text())
        services = config['services']
        ports = set()
        for name in ['sgacd', 'analematica', 'erp-tur', 'turismo']:
            service = services[name]
            self.assertEqual(service['env_file'], ['./.runtime/' + name + '.env'])
            self.assertIn('127.0.0.1', service['ports'][0])
            ports.add(service['ports'][0])
            self.assertNotIn('container_name', service)
        self.assertEqual(len(ports), 4)
        for name in ['sgacd-db', 'erp-tur-db', 'turismo-db', 'redis']:
            self.assertNotIn('ports', services[name])
        self.assertNotIn('privileged', json.dumps(config))

class CorporateGatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gateway = load('corporate_local_gateway', ROOT / 'BACKEND/ANALEMATICA-BACKEND/deployment/api.py')

    def request(self, path, responder, method='GET', **kwargs):
        import httpx
        from fastapi.testclient import TestClient
        with TestClient(self.gateway.app) as client:
            original = self.gateway.app.state.upstream
            mock = httpx.AsyncClient(base_url=self.gateway.UPSTREAM, transport=httpx.MockTransport(responder))
            self.gateway.app.state.upstream = mock
            try:
                return client.request(method, path, **kwargs)
            finally:
                client.portal.call(mock.aclose)
                self.gateway.app.state.upstream = original

    def test_preserves_authentication_errors(self):
        def responder(request):
            self.assertEqual(request.headers['authorization'], 'Bearer test-only')
            self.assertNotIn('x-secret-test', request.headers)
            self.assertEqual(request.url.path, '/api/v1/workspace/corporate/session')
            return __import__('httpx').Response(401, json={'detail': 'No autorizado'})
        response = self.request('/api/v1/workspace/corporate/session', responder, headers={'Authorization': 'Bearer test-only', 'X-Secret-Test': 'do-not-forward'})
        self.assertEqual(response.status_code, 401)

    def test_forwards_query_body_and_cookies_without_redirects(self):
        import httpx
        def responder(request):
            self.assertEqual(request.url.query, b'key=1&key=2')
            self.assertEqual(json.loads(request.content), {'revision': 2})
            self.assertEqual(request.headers['cookie'], 'session=test-only')
            return httpx.Response(409, json={'detail': 'Revision conflict'}, headers={'X-Correlation-ID': 'test-id'})
        response = self.request('/api/v1/workspace/corporate/config?key=1&key=2', responder, method='PUT', json={'revision': 2}, headers={'Cookie': 'session=test-only'})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.headers['x-correlation-id'], 'test-id')

    def test_health_fails_when_dependency_is_unavailable(self):
        import httpx
        response = self.request('/healthz', lambda req: httpx.Response(503))
        self.assertEqual(response.status_code, 503)

    def test_internal_source_files_are_not_served(self):
        import httpx
        response = self.request('/deployment/api.py', lambda req: httpx.Response(200))
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
