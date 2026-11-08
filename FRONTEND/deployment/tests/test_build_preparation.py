"""Full source build preparation must preserve strict checking and original sources."""
import importlib.util,tempfile,unittest,json
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('build_preview',HERE/'prepare.py');preview=importlib.util.module_from_spec(spec);spec.loader.exec_module(preview)
class BuildPreparationTests(unittest.TestCase):
 def test_isolated_full_sources_and_explicit_dependencies(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory)
   with patch.object(preview,'RUNTIME',root):preview.next_projects(dependencies=root/'deps',systems=('erp',))
   project=root/'erp'
   self.assertEqual((project/'node_modules').readlink(),root/'deps')
   self.assertTrue((project/'src/app/erp/cotizaciones/page.tsx').is_file())
   self.assertTrue((project/'src/app/dashboard/prestador/mi-negocio/gestion-comercial/cotizaciones/PasswordRecovery.tsx').is_file())
   config=(project/'next.config.mjs').read_text();self.assertNotIn('ignoreBuildErrors',config);self.assertNotIn('ignoreDuringBuilds',config)
   self.assertTrue(json.loads((project/'tsconfig.json').read_text())['compilerOptions']['strict'])
   self.assertFalse((root/'turismo').exists())
 def test_unknown_system_is_rejected(self):
  with tempfile.TemporaryDirectory() as directory,patch.object(preview,'RUNTIME',Path(directory)):
   with self.assertRaises(ValueError):preview.next_projects(systems=('unknown',))
 def test_institutional_shared_erp_modules_do_not_add_erp_routes(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory)
   with patch.object(preview,'RUNTIME',root):preview.next_projects(dependencies=root/'deps',systems=('turismo',))
   project=root/'turismo'
   self.assertTrue((project/'src/shared/erp/hooks/useMiNegocioApi.ts').is_file())
   self.assertFalse((project/'src/app/dashboard/prestador/mi-negocio').exists())
   self.assertEqual(json.loads((project/'tsconfig.json').read_text())['compilerOptions']['paths']['@/app/dashboard/prestador/mi-negocio/*'],['./src/shared/erp/*'])
   self.assertNotIn(str(root),(project/'next.config.mjs').read_text())
if __name__=='__main__':unittest.main()
