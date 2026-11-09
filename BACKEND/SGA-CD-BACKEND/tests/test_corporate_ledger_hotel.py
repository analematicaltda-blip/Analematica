"""Both real APIs: recorded room capacity and classified ledger KPIs, synthetic only."""
import os,unittest
from unittest.mock import patch
import test_corporate_ledger_integration as integration
class CorporateHotelTests(unittest.TestCase):
 login=integration.DualLedgerIntegration.login
 tearDown=integration.DualLedgerIntegration.tearDown
 command=integration.DualLedgerIntegration.command
 def setUp(self):
  env=patch.dict(os.environ,{'HOTEL_BROWSER':'1'});env.start();self.addCleanup(env.stop);integration.DualLedgerIntegration.setUp(self)
 def test_two_confirmations_and_actual_shared_ledger_hotel_ratios(self):
  source=self.client.get('/api/v1/workspace/corporate/accounting/sources/hotel_sources');self.assertEqual(source.status_code,200,source.text);self.assertEqual(len(source.json()['rooms']),2)
  args=self.credentials['hotel'];review=self.command('review_hotel_capacity',args);self.assertEqual(review.status_code,200,review.text)
  body={'review_id':review.json()['data']['review_id'],'confirmed':False};self.assertEqual(self.command('record_hotel_capacity',body).status_code,422);body['confirmed']=True
  recorded=self.command('record_hotel_capacity',body);self.assertEqual(recorded.status_code,200,recorded.text);self.assertFalse(recorded.json()['data']['ledger_written']);self.assertTrue(self.command('record_hotel_capacity',body).json()['data']['replayed'])
  params={'since':self.day,'until':self.day};r=self.client.get('/api/v1/workspace/corporate/accounting/sources/hotel_metrics',params=params);self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['revpar'],'5.0000');self.assertEqual(r.json()['goppar'],'4.0000');self.assertEqual(r.json()['available_room_days'],2)
  direct=self.unwrap(self.erp.get(integration.bridge.BASE+'indicadores-hoteleros/',params={**params,'provider_id':self.provider,'as_of':r.json()['as_of']}).json());self.assertEqual(direct,r.json());self.assertFalse(r.json()['ledger_written']);self.assertIsNone(r.json()['package_margin'])
if __name__=='__main__':unittest.main()
