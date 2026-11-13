"""Delivery contract for private marketing media and scoped quote links."""
import importlib.util,unittest,tempfile,os
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('quote_preview_delivery',HERE/'prepare.py');preview=importlib.util.module_from_spec(spec);spec.loader.exec_module(preview)
class QuoteDeliveryTests(unittest.TestCase):
 def config(self,enabled):
  with tempfile.TemporaryDirectory() as tmp,patch.object(preview,'RUNTIME',Path(tmp)),patch.dict(os.environ,{'SGACD_ENABLE_ERP_API':'1' if enabled else '0'}):
   preview.nginx();return (Path(tmp)/'nginx.conf').read_text()
 def test_blob_media_is_allowed_without_blob_scripts_or_frames(self):
  config=self.config(True);self.assertIn("img-src 'self' data: blob: https:",config);self.assertIn("media-src 'self' blob:",config);self.assertIn("frame-ancestors 'none'",config);self.assertNotIn("script-src 'self' blob:",config)
 def test_only_opted_in_erp_routes_get_media_limit_and_quote_link_proxy(self):
  config=self.config(True);self.assertIn('location ^~ /api/v1/mi-negocio/comercial/unified/crm/quotation-media/ { client_max_body_size 256k;',config);self.assertIn('location ^~ /api/v1/mi-negocio/comercial/unified/crm/ { client_max_body_size 16k;',config);self.assertIn('unified/quote-links/[0-9a-f-]+/[0-9a-f-]+',config);self.assertIn('Ruta ERP pendiente de validación.',config);self.assertEqual(config.count('location = /commercial-quote.html { auth_basic off;'),3);self.assertIn('auth_basic "Vista local erp"',config)
  disabled=self.config(False);self.assertNotIn('unified/quote-links/',disabled);self.assertNotIn('unified/crm/quotation-media/',disabled)
 def test_private_recipient_assets_and_new_routes_are_in_prepared_erp(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(preview,'RUNTIME',Path(tmp)):
   preview.next_projects(dependencies=Path(tmp)/'deps',systems=('erp',));root=Path(tmp)/'erp'
   for name in ('commercial-quote.html','js/commercial-quote-recipient.js','js/commercial-quotations.js'):self.assertTrue((root/'public'/name).is_file())
   self.assertTrue((root/'src/app/dashboard/prestador/mi-negocio/gestion-comercial/cotizaciones-dinamicas/page.tsx').is_file());self.assertTrue((root/'src/app/dashboard/prestador/mi-negocio/gestion-comercial/cotizaciones/PasswordRecovery.tsx').is_file())
if __name__=='__main__':unittest.main()
