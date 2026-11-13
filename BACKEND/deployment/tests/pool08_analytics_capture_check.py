"""Real landing submission, declared UTM, current consent and withdrawal."""
import runpy,unittest,importlib,html,re
from pathlib import Path
f=runpy.run_path(str(Path(__file__).with_name('pool08_capture_native_check.py')),run_name='analytics_capture_setup')
suite=unittest.TestSuite()
for name,path in [('ERP','apps.prestadores.mi_negocio.gestion_comercial.pool08'),('Ana','apps.admin_plataforma.gestion_comercial.pool08')]:
 class Checks(f[name]):
  module_path=path
  def test_analytics_real_capture_and_withdrawal_are_not_provider_attribution(self):
   self.data['marketing']='yes';page=self.handler.form(self.ref,self.browser,{'utm_source':'meta','utm_campaign':'declared-campaign'},'/capture/','https://example.test/page');self.data['token']=html.unescape(re.search('name="token" value="([^"]+)"',page).group(1));result=self.submit();sources=importlib.import_module(self.module_path+'.analytics_sources');people=sources.contacts(self.handler.crm);r=sources.attribution(self.handler.crm,people);self.assertEqual(len(r['groups']),1);g=r['groups'][0];self.assertEqual(g['declared_channel'],'meta');self.assertEqual(g['contacts'],1);self.assertFalse(g['provider_attribution_verified']);self.handler.withdraw(self.ref,result['reference'],result['withdrawal_proof']);r=sources.attribution(self.handler.crm,sources.contacts(self.handler.crm));self.assertEqual(r['groups'],[]);self.assertEqual(r['excluded_withdrawn_contacts'],1)
 suite.addTest(Checks('test_analytics_real_capture_and_withdrawal_are_not_provider_attribution'))
if __name__=='__main__':raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
