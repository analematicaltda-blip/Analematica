import unittest,sys,io
from pathlib import Path
from contextlib import redirect_stdout
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.services.email_service import EmailService
class Checks(unittest.TestCase):
 def test_unconfigured_legacy_service_does_not_claim_delivery_or_print_recipient(self):
  output=io.StringIO()
  with redirect_stdout(output):result=EmailService().send_transactional_email('private@example.test','Private subject','Private message')
  self.assertFalse(result);self.assertEqual(output.getvalue(),'')
if __name__=='__main__':unittest.main()
