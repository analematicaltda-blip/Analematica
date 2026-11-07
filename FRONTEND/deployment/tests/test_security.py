import importlib.util
import json
import os
from pathlib import Path
import ssl
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('local_preview', HERE / 'prepare.py')
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)

class PreviewSecurityTests(unittest.TestCase):
    def test_access_is_distinct_hashed_private_and_stable(self):
        import bcrypt
        with tempfile.TemporaryDirectory() as temp, patch.object(preview, 'PRIVATE', Path(temp)):
            before = preview.credentials()
            after = preview.credentials()
            self.assertEqual(before, after)
            self.assertEqual(len({v['password'] for v in before.values()}), 4)
            for name, account in before.items():
                stored = (Path(temp) / (name + '.htpasswd')).read_text().strip()
                user, hashed = stored.split(':', 1)
                self.assertEqual(user, account['username'])
                self.assertTrue(bcrypt.checkpw(account['password'].encode(), hashed.encode()))
                self.assertNotIn(account['password'], stored)
            if os.name != 'nt':
                self.assertTrue(all(p.stat().st_mode & 0o077 == 0 for p in Path(temp).iterdir()))

    def test_certificate_is_local_only_and_is_not_replaced(self):
        from cryptography import x509
        with tempfile.TemporaryDirectory() as temp, patch.object(preview, 'PRIVATE', Path(temp)):
            preview.certificate()
            original = (Path(temp) / 'localhost.key').read_bytes()
            preview.certificate()
            self.assertEqual(original, (Path(temp) / 'localhost.key').read_bytes())
            cert = x509.load_pem_x509_certificate((Path(temp) / 'localhost.crt').read_bytes())
            names = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
            self.assertEqual(names.get_values_for_type(x509.DNSName), ['localhost'])
            self.assertEqual([str(x) for x in names.get_values_for_type(x509.IPAddress)], ['127.0.0.1'])

    def test_public_copy_does_not_publish_source_or_private_directories(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(preview, 'RUNTIME', Path(temp)):
            preview.public_assets()
            for name in ['sgacd', 'analematica']:
                folder = Path(temp) / 'sites' / name
                self.assertTrue((folder / 'login.html').exists())
                self.assertFalse(any(p.name in ['docs', 'tests', 'deployment', '.env', 'private'] for p in folder.rglob('*')))
                self.assertFalse(list(folder.rglob('*.py')))
            self.assertIn('location.origin', (Path(temp) / 'sites/sgacd/js/config.js').read_text())

    def test_only_ingress_publishes_loopback_ports_and_no_credentials_enter_compose(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(preview, 'HERE', Path(temp)):
            preview.compose()
            data = json.loads((Path(temp) / 'compose.yaml').read_text())
            for name, service in data['services'].items():
                self.assertTrue(service['read_only'])
                self.assertEqual(service['cap_drop'], ['ALL'])
                if name == 'web':
                    self.assertTrue(all(value.startswith('127.0.0.1:') for value in service['ports']))
                else:
                    self.assertNotIn('ports', service)
                    self.assertEqual(service['environment']['NEXT_PUBLIC_ENABLE_MOCKS'], 'false')
                    self.assertFalse(any('/private:' in value for value in service['volumes']))

if __name__ == '__main__':
    unittest.main()
