"""SGA media scope, quotas, rollback and revoked permissions in its own actual ORM."""
import runpy,unittest,uuid,base64,json,io
from pathlib import Path
from unittest.mock import patch
from PIL import Image
f=runpy.run_path(str(Path(__file__).with_name('test_pool08_landings.py')),run_name='library_sga_setup')
from app.commercial.pool08.library_models import LibraryItem,LibraryEvent,LibraryBlob
from app.models.user import Usuario
class Checks(unittest.TestCase):
 def setUp(self):
  f['Checks'].setUp(self)
  for model in (LibraryItem,LibraryEvent,LibraryBlob):model.__table__.create(self.db.get_bind(),checkfirst=True)
  b=io.BytesIO();Image.new('RGB',(30,20)).save(b,format='PNG');self.raw=b.getvalue();self.meta={'title':'Pieza','classification':'MARKETING','brand':{'name':'Propia','tagline':'Marca','template':'STORY'},'rights':{'holder':'Titular','license':'OWNED','reference':'Declaración de prueba','valid_until':None,'public_web':True}}
 tearDown=f['Checks'].tearDown;login=f['Checks'].login
 def upload(self,body=None):
  body=body or {'request_id':str(uuid.uuid4()),'item_id':None,'expected_revision':0,'metadata':self.meta};return self.client.post('/api/v1/commercial-unified/crm/library-upload',content=self.raw,headers={'Content-Type':'image/png','X-Library-Metadata':base64.b64encode(json.dumps(body).encode()).decode()})
 def get(self,path):return self.client.get('/api/v1/commercial-unified/crm/'+path)
 def command(self,op,ref,rev,**data):return self.client.post('/api/v1/commercial-unified/crm/library-commands',json={'request_id':str(uuid.uuid4()),'operation':op,'item_id':ref,'expected_revision':rev,'data':data})
 def test_event_failure_rolls_back_blob_and_item(self):
  from app.commercial.pool08.library_store import Store
  with patch.object(Store,'append',side_effect=RuntimeError('synthetic event failure')):
   with self.assertRaises(RuntimeError):self.upload()
  self.assertEqual(self.db.query(LibraryItem).count(),0);self.assertEqual(self.db.query(LibraryBlob).count(),0)
 def test_foreign_scope_cannot_download_publish_or_recover_receipt(self):
  b={'request_id':str(uuid.uuid4()),'item_id':None,'expected_revision':0,'metadata':self.meta};r=self.upload(b);self.assertEqual(r.status_code,200,r.text);ref=r.json()['item_id'];self.login('other-admin_empresa');self.assertEqual(self.get('library/'+ref+'/versions/1/original').status_code,404);self.assertEqual(self.command('approve',ref,1,rights_confirmed=True,privacy_reviewed=True).status_code,404);self.assertEqual(self.get('library-receipts/'+b['request_id']).status_code,404)
 def test_revoked_publisher_cannot_read_or_serve_public_copy(self):
  ref=self.upload().json()['item_id'];self.assertEqual(self.command('approve',ref,1,rights_confirmed=True,privacy_reviewed=True).status_code,200);self.assertEqual(self.command('publish',ref,2,confirmed=True).status_code,200);user=self.db.get(Usuario,self.users['full-admin_empresa']);user.roles=[];user.rol='jefe_area';self.db.commit();self.assertEqual(self.get('library/'+ref).status_code,403);self.assertEqual(self.client.get('/api/v1/commercial-unified/media-library/'+ref+'/1',headers={'Authorization':''}).status_code,404)
 def test_quota_counts_original_and_delivery_and_blocks_extra_upload(self):
  from app.commercial.pool08.library_store import Store
  ref=self.upload().json()['item_id'];item=self.get('library/'+ref).json();v=item['versions'][0];usage=self.get('library').json()['usage'];self.assertEqual(usage['bytes'],v['original_size']+v['delivery_size']);self.assertEqual(usage['originals'],1)
  with patch.object(Store,'usage',return_value=(200,0)):self.assertEqual(self.upload().status_code,413)
  self.assertEqual(self.db.query(LibraryBlob).count(),1)
 def test_corrupt_blob_is_rejected(self):
  ref=self.upload().json()['item_id'];row=self.db.query(LibraryBlob).one();row.delivery=b'changed';self.db.commit();self.assertEqual(self.get('library/'+ref+'/versions/1/delivery').status_code,503);self.assertEqual(self.get('library/'+ref+'/versions/1/original').content,self.raw)
if __name__=='__main__':unittest.main()
