import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('prepare_meta', ROOT.parent/'backend/deployment/prepare_meta.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class MetaSetupTests(unittest.TestCase):
    def test_codespace_detection(self):
        self.assertEqual(module.resolve_origin(environ={'CODESPACE_NAME':'my-space'}), 'https://my-space-8090.app.github.dev')
    def test_origin_validation(self):
        for origin in ['http://example.com', 'https://example.com/a', 'https://user:pass@example.com', 'https://example.com?token=bad']:
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                module.resolve_origin(origin, environ={})
    def test_no_invented_public_address(self):
        with self.assertRaises(ValueError): module.resolve_origin(environ={})
    def test_separate_configs_and_no_secrets(self):
        config=json.loads((ROOT/'config/meta-public.json').read_text())
        self.assertNotEqual(config['user_login_config_id'],config['instagram_system_login_config_id'])
        self.assertFalse(any('secret' in k or 'token' in k for k in config))

if __name__=='__main__': unittest.main()
