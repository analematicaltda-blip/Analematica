"""Behavioral cases shared only by tests; production modules remain independently owned."""
import uuid,io,copy,os
from datetime import datetime,timezone,timedelta
from pool08_pricing_cases import PricingCases
from PIL import Image
class QuotationCases:
 price_values=PricingCases.values
 price_body=PricingCases.body
 def body(self,operation='create',ref=None,revision=0,**data):return dict(request_id=str(uuid.uuid4()),operation=operation,quotation_id=ref,expected_revision=revision,data=data)
 def price(self):
  r=self.price_call(self.price_body(**self.price_values()));self.assertEqual(r.status_code,200,self.data(r));return self.data(r)['item_id']
 def policy(self,ref,mode='NOT_APPLICABLE',resource=None):
  r=self.call('post',self.body('review_capacity',item_id=ref,price_revision=1,mode=mode,resource_ref=resource,reason='Revisión declarada de capacidad',support_digest='a'*64));self.assertEqual(r.status_code,200,self.data(r));return self.data(r)
 def values(self,ref,**extra):
  data=dict(title='Cotización de prueba',contact_id=self.contact,opportunity_id=None,offer=dict(currency='COP',lines=[dict(item_id=ref,revision=1,quantity='1',discount_bps=0)]),terms='Condiciones de prueba autorizadas en laboratorio',expires_at=(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),media_ids=[],service_windows=[]);data.update(extra);return data
 def create(self,ref=None,policy=True,**extra):
  ref=ref or self.price()
  if policy:self.policy(ref)
  r=self.call('post',self.body(**self.values(ref,**extra)));self.assertEqual(r.status_code,200,self.data(r));return self.data(r)['quotation_id']
 def issue(self,ref,rev=1):
  r=self.call('post',self.body('issue',ref,rev));self.assertEqual(r.status_code,200,self.data(r));return self.data(r)
 def link(self,ref,rev=2):
  r=self.call('post',self.body('link',ref,rev,confirm_share=True));self.assertEqual(r.status_code,200,self.data(r));return self.data(r)
 def acceptance(self,ref):
  record=self.data(self.call(ref=ref));return dict(request_id=str(uuid.uuid4()),version=record['version'],content_digest=record['content_digest'],confirmed=True)
 def test_issue_link_accept_version_and_replay_no_financial_effect(self):
  ref=self.create();self.issue(ref);link=self.link(ref);view=self.data(self.public(ref,link));self.assertEqual(view['content']['estimate']['total'],'14691.35');self.assertNotIn('contact_id',view['content']);body=self.acceptance(ref);a=self.public(ref,link,body);self.assertEqual(a.status_code,200,self.data(a));self.assertTrue(self.data(self.public(ref,link,body))['replayed']);self.assertEqual(self.public(ref,link,self.acceptance(ref)).status_code,409)
  record=self.data(self.call(ref=ref));self.assertEqual(record['status'],'ACCEPTED');self.assertFalse(record['acceptance']['customer_identity_verified']);self.assertEqual(record['acceptance']['content_digest'],body['content_digest'])
  for k in ('payment_verified','ledger_written','reservation_created','capacity_reserved'):self.assertFalse(record[k])
 def test_price_changed_blocks_issue_or_accept(self):
  price=self.price();ref=self.create(price);self.price_call(self.price_body('update',price,1,unit_price='1.00'));self.assertEqual(self.call('post',self.body('issue',ref,1)).status_code,409)
  price=self.price();ref=self.create(price);self.issue(ref);link=self.link(ref);self.price_call(self.price_body('update',price,1,unit_price='1.00'));self.assertEqual(self.public(ref,link,self.acceptance(ref)).status_code,409);self.assertEqual(self.data(self.call(ref=ref))['status'],'ISSUED')
 def test_capacity_policy_missing_blocks_issue(self):
  ref=self.create(policy=False);self.assertEqual(self.call('post',self.body('issue',ref,1)).status_code,409)
 def test_wrong_token_version_and_internal_accept_command(self):
  ref=self.create();self.issue(ref);link=self.link(ref);wrong={**link,'link_token':'0'*64};self.assertEqual(self.public(ref,wrong).status_code,403);body=self.acceptance(ref);body['version']=99;self.assertEqual(self.public(ref,link,body).status_code,409);self.assertEqual(self.call('post',self.body('accept',ref,3,confirmed=True)).status_code,422)
 def test_revise_invalidates_old_link_retains_history(self):
  price=self.price();ref=self.create(price);self.issue(ref);link=self.link(ref);r=self.call('post',self.body('revise',ref,3,**self.values(price,title='Versión revisada')));self.assertEqual(r.status_code,200,self.data(r));record=self.data(self.call(ref=ref));self.assertEqual(record['version'],2);self.assertEqual(record['status'],'DRAFT');self.assertEqual(self.public(ref,link).status_code,403);history=self.data(self.call(ref=ref,section='history'));self.assertTrue(history['history_verified']);self.assertEqual(history['events'][0]['snapshot']['content']['title'],'Cotización de prueba')
 def test_withdrawal_and_stale_revision(self):
  ref=self.create();self.issue(ref);link=self.link(ref);self.assertEqual(self.call('post',self.body('withdraw',ref,1,reason='Vieja')).status_code,409);self.assertEqual(self.call('post',self.body('withdraw',ref,3,reason='Retirada')).status_code,200);self.assertEqual(self.public(ref,link).status_code,403)
 def test_idempotent_create_and_token_not_stored_in_document_or_history(self):
  price=self.price();self.policy(price);body=self.body(**self.values(price));one=self.data(self.call('post',body));two=self.data(self.call('post',body));self.assertEqual(one['quotation_id'],two['quotation_id']);self.assertTrue(two['replayed']);ref=one['quotation_id'];self.issue(ref);link=self.link(ref)
  import json
  self.assertNotIn(link['link_token'],json.dumps(self.data(self.call(ref=ref))));self.assertNotIn(link['link_token'],json.dumps(self.data(self.call(ref=ref,section='history'))))
 def test_wrong_media_type_and_image_content_integrity(self):
  ref=str(uuid.uuid4());self.assertEqual(self.upload(ref,b'<svg onload="alert(1)"/>','image/svg+xml').status_code,415);self.assertEqual(self.upload(ref,b'garbage','image/png').status_code,422)
  image=io.BytesIO();Image.new('RGB',(12,12),(10,30,60)).save(image,format='PNG');raw=image.getvalue();response=self.upload(ref,raw,'image/png');self.assertEqual(response.status_code,200,self.data(response));self.assertTrue(self.data(self.upload(ref,raw,'image/png'))['replayed']);image=io.BytesIO();Image.new('RGB',(12,12),'red').save(image,format='PNG');self.assertEqual(self.upload(ref,image.getvalue(),'image/png').status_code,409)
  quote=self.create(media_ids=[ref]);self.issue(quote);link=self.link(quote);media=self.public(quote,link,asset=ref);self.assertEqual(media.status_code,200);self.assertEqual((media.headers if hasattr(media,'headers') else media)['Content-Type'].split(';')[0],'image/png')
 def test_missing_link_key_never_uses_default(self):
  from unittest.mock import patch
  ref=self.create();self.issue(ref)
  with patch.dict(os.environ,{'COMMERCIAL_QUOTE_LINK_KEY':''}):self.assertEqual(self.call('post',self.body('link',ref,2,confirm_share=True)).status_code,503)
 def test_price_and_total_forgery_and_expired_draft(self):
  price=self.price();data=self.values(price);data['offer']['lines'][0]['unit_price']='0.00';self.assertEqual(self.call('post',self.body(**data)).status_code,422);self.assertEqual(self.call('post',self.body(**self.values(price,expires_at=(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()))).status_code,422)

 def test_video_is_private_bounded_and_verified(self):
  import subprocess,tempfile
  from pathlib import Path
  with tempfile.TemporaryDirectory(prefix='quote-video-test-') as tmp:
   path=Path(tmp)/'clip.mp4';subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=blue:s=160x90:d=1','-c:v','libx264','-pix_fmt','yuv420p','-y',str(path)],capture_output=True,timeout=10,check=True);raw=path.read_bytes()
  asset=str(uuid.uuid4());r=self.upload(asset,raw,'video/mp4');self.assertEqual(r.status_code,200,self.data(r));self.assertEqual(self.data(r)['mime'],'video/mp4');self.assertEqual(self.upload(str(uuid.uuid4()),b'x'*262145,'video/mp4').status_code,413)
 def test_quote_expiry_blocks_acceptance_and_malformed_offer_is_rejected(self):
  from unittest.mock import patch
  ref=self.create();self.issue(ref);link=self.link(ref)
  with patch(self.domain_path+'.quotations.datetime') as clock:
   clock.now.return_value=datetime.now(timezone.utc)+timedelta(days=2)
   self.assertEqual(self.public(ref,link,self.acceptance(ref)).status_code,403)
  price=self.price();self.assertEqual(self.call('post',self.body(**self.values(price,offer=None))).status_code,422)
