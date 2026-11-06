"""Dedicated REVIEW-1 regressions; real authenticated HTTP and browser fixtures."""
import copy,http.client,json,os,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from test_rooms import RoomFixture

class DesignReviewHTTPTests(unittest.TestCase):
 def setUp(self):self.f=RoomFixture()
 def tearDown(self):self.f.close()
 def raw_post(self,url,value):
  f=self.f;csrf=f.request('GET','/api/session')[1]['csrf'];c=http.client.HTTPConnection('127.0.0.1',f.port,timeout=10)
  try:
   c.request('POST',url,json.dumps(value),{'X-Remote-User-Id':'alice','X-LUMO-Read':'1','X-LUMO-Action':'1','X-LUMO-CSRF':csrf,'Origin':f.origin,'Content-Type':'application/json'})
   try:r=c.getresponse()
   except http.client.RemoteDisconnected:self.fail('Authenticated design POST disconnected instead of bounded JSON rejection')
   raw=r.read();self.assertIn('application/json',r.getheader('Content-Type'));return r.status,raw
  finally:c.close()
 def stored_bytes(self,id):
  with self.f.store.connect() as c:return c.execute('SELECT revision,document FROM dashboards WHERE id=?',(id,)).fetchone()
 def test_b1_extreme_integer_rejection_preserves_document_and_opaque_numbers(self):
  f=self.f;big=int('9'*400);native={'views':[{'title':'Opaque integer fixture','cards':[{'type':'custom:protected','positive':big,'negative':-big}]}]}
  d=f.store.import_native('alice','B1 fixture',native);url='/api/dashboards/'+d['id'];base=f.request('GET',url+'/design')[1]['design'];before=self.stored_bytes(d['id'])
  fields=[('display',k,lo,hi) for k,lo,hi in [('width',320,3840),('height',240,2160),('dpr',.5,4),('diagonal',3,150),('hardwareWidth',240,16384),('hardwareHeight',240,16384)]]+[('override','radius',0,40),('override','shadow',0,40),('override','weight',400,700),('root','schemaVersion',1,1)]
  def changed(area,key,value):
   v=copy.deepcopy(base);target=v['displays']['desktop'] if area=='display' else v['overrides'] if area=='override' else v;target[key]=value;return v
  for area,key,lo,hi in fields:
   for value in (big,-big,True,float('nan'),float('inf'),float('-inf')):
    with self.subTest(field=key,value=str(value)[:20]):
     status,raw=self.raw_post(url+'/design',{'revision':d['revision'],'design':changed(area,key,value)})
     self.assertEqual(status,400);self.assertLess(len(raw),1024);self.assertIsInstance(json.loads(raw)['error'],str);self.assertEqual(self.stored_bytes(d['id']),before);self.assertEqual(f.request('GET',url)[1],d)
  # Valid boundary saves still succeed; the opaque native integers stay exact.
  for area,key,lo,hi in fields:
   for value in (lo,hi):
    with self.subTest(boundary=key,value=value):
     status,saved=f.post(url+'/design',{'revision':d['revision'],'design':changed(area,key,value)});self.assertEqual(status,200,saved);self.assertEqual(saved['revision'],d['revision']+1);d=saved
     self.assertEqual(f.request('GET',url+'/export')[1],native);self.assertEqual(d['native'],native)
  from design import validate
  from store import StudioError
  for value in (float('nan'),float('inf'),float('-inf')):
   with self.subTest(directNonfinite=str(value)),self.assertRaises(StudioError):validate(changed('display','dpr',value))

if __name__=='__main__':unittest.main()
