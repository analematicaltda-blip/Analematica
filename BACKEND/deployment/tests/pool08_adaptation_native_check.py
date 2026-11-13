import runpy,unittest
from pathlib import Path
from pool08_adaptation_cases import AdaptationCases
f=runpy.run_path(str(Path(__file__).with_name('pool08_generation_native_check.py')),run_name='adaptation_native_setup');suite=unittest.TestSuite()
for system,path in [('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08'),('analematica','apps.admin_plataforma.gestion_comercial.pool08')]:
 base=f['cases'](system,path)
 class Checks(AdaptationCases,base):pass
 suite.addTests(Checks(name) for name in unittest.defaultTestLoader.getTestCaseNames(AdaptationCases))
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
