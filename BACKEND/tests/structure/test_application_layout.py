"""The four application layers own their code; reports retain their own locations."""
from pathlib import Path
import configparser
import unittest
ROOT=Path(__file__).resolve().parents[3]
class ApplicationLayout(unittest.TestCase):
 def test_legacy_application_roots_are_empty(self):
  for name in ('scripts','tests','infra','DB','SEGURIDAD','Skill.git','skills-contabilidad','Conta-Skills','audittor','llm','colibri','matrix-os','Analematica','deploy_military_army.py','design_tokens.json'):
   with self.subTest(name=name):self.assertFalse((ROOT/name).exists())
 def test_application_code_has_a_layer_owner(self):
  for name in ('BACKEND/DB','BACKEND/infra/node6','BACKEND/SEGURIDAD','BACKEND/IA/llm','BACKEND/herramientas/audittor','BACKEND/Skill.git','BACKEND/Analematica','BACKEND/tools/start_node6.py','FRONTEND/tools/render_landing.py','FRONTEND/design_tokens.json','FRONTEND/tests','DESKTOP/tools/flet_preview','DESKTOP/tests/flet','DESKTOP/matrix-os','MOVILES/WALLET-MOVIL'):
   with self.subTest(name=name):self.assertTrue((ROOT/name).exists())
 def test_reports_and_single_tracking_record_remain_in_place(self):
  for name in ('ANALISIS/gestion-comercial/plan-pool08.json','ANALISIS/contabilidad/CIERRE_20_HITOS.md','INTEGRACIONES/plan-maestro/auditoria-bloque01/HALLAZGOS_Y_PRIORIDADES.md'):
   self.assertTrue((ROOT/name).is_file())
  self.assertFalse(list((ROOT/'INTEGRACIONES').rglob('*.py')))
 def test_submodule_paths_follow_their_layers(self):
  configuration=configparser.ConfigParser();configuration.read(ROOT/'.gitmodules')
  self.assertEqual(configuration['submodule "colibri"']['path'],'BACKEND/servicios/colibri')
  self.assertEqual(configuration['submodule "matrix-os"']['path'],'DESKTOP/matrix-os')
if __name__=='__main__':unittest.main(verbosity=2)
