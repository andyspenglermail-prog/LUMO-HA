"""Optional stable-view image bindings through actual HTTP and SQLite."""
import copy,json,pathlib,sys,unittest,base64,sqlite3
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from test_rooms import RoomFixture
from test_images import png
class RoomPhotoStoreTests(unittest.TestCase):
 def setUp(self):self.f=RoomFixture()
 def tearDown(self):self.f.close()
 def test_owned_binding_persists_without_touching_original_or_background(self):
  f=self.f;d=f.store.import_native('alice','Photos fixture',{'views':[{'title':'Same','cards':[{'type':'custom:keep','large':9007199254740993,'flag':True,'float':1.0}]},{'title':'Same','cards':[]}]});url='/api/dashboards/'+d['id'];view,other=[v['id'] for v in d['views']]
  from native import compile_native
  original=json.dumps(compile_native(f.store,'alice',d),ensure_ascii=True,indent=2).encode()
  image=f.post('/api/images',{'name':'Synthetic.png','data':base64.b64encode(png()).decode()})[1];design=f.request('GET',url+'/design')[1]['design'];design['roomImages']={view:image['id']}
  status,saved=f.post(url+'/design',{'revision':d['revision'],'design':design});self.assertEqual(status,200,saved);self.assertEqual(saved['design']['roomImages'],{view:image['id']})
  for k in ('native','nativeImport','views','settings'):self.assertEqual(saved[k],d[k])
  self.assertEqual(json.dumps(compile_native(f.store,'alice',saved),ensure_ascii=True,indent=2).encode(),original)
  self.assertEqual(f.post(url+'/design',{'revision':d['revision'],'design':design})[0],409)
  self.assertEqual(f.post(url+'/design',{'revision':saved['revision'],'design':design},user='bob')[0],404)
  self.assertEqual(f.request('POST',url+'/design',{'revision':saved['revision'],'design':design})[0],403)
  foreign=f.store.put_image('bob','Foreign',png('blue'));invalid=[None,[],{'':image['id']},{'__proto__':image['id']},{view:None},{view:True},{view:'https://invalid.example/x'},{view:'a'*32},{view:foreign['id']},{'b'*32:image['id']},{view:{'imageId':image['id']}}]
  for value in invalid:
   bad=copy.deepcopy(design);bad['roomImages']=value
   with self.subTest(value=value):
    self.assertIn(f.post(url+'/design',{'revision':saved['revision'],'design':bad})[0],(400,404));self.assertEqual(f.store.get('alice',d['id']),saved)
  from store import Store
  from maintenance import backup,restore
  snap=f.root/'photos.sqlite';backup(f.store.path,snap);self.assertEqual(Store(f.store.path).get('alice',d['id']),saved);f.stop();f.store=Store(f.store.path);f.start();self.assertEqual(f.request('GET',url+'/design')[1]['design'],saved['design'])
  copied=f.store.duplicate('alice',d['id'],saved['revision']);self.assertEqual(copied['design'],design);design['roomImages']={};changed=f.post(url+'/design',{'revision':saved['revision'],'design':design})[1];self.assertEqual(changed['design']['roomImages'],{});self.assertEqual(f.store.get('alice',copied['id'])['design']['roomImages'],{view:image['id']});restore(snap,f.store.path);self.assertEqual(Store(f.store.path).get('alice',d['id']),saved)
  legacy=copy.deepcopy(design);del legacy['roomImages'];self.assertEqual(f.post(url+'/design',{'revision':saved['revision'],'design':legacy})[0],200)
 def test_maintenance_rejects_foreign_missing_and_dangling_photo_references(self):
  from design import defaults,save
  from maintenance import inspect
  f=self.f;d=f.store.import_native('alice','Inspect fixture',{'views':[{'title':'View','cards':[]}]});view=d['views'][0]['id'];image=f.store.put_image('alice','Owned',png());foreign=f.store.put_image('bob','Foreign',png());design=defaults();design['roomImages']={view:image['id']};d=save(f.store,'alice',d['id'],d['revision'],design)
  for binding in ({view:foreign['id']},{view:'a'*32},{'b'*32:image['id']}):
   bad=copy.deepcopy(d);bad['design']['roomImages']=binding
   with f.store.connect() as c:c.execute('UPDATE dashboards SET document=? WHERE id=?',(json.dumps(bad),d['id']))
   with self.subTest(binding=binding),self.assertRaises(Exception):inspect(f.store.path)
  with f.store.connect() as c:c.execute('UPDATE dashboards SET document=? WHERE id=?',(json.dumps(d),d['id']))
  self.assertEqual(inspect(f.store.path),2)
 def test_stable_bindings_survive_rename_reorder_hidden_and_confirmed_delete(self):
  from design import defaults,save
  from room_store import save_plan,get_plan
  from maintenance import inspect
  f=self.f;d=f.store.import_native('alice','Stable fixture',{'views':[{'title':'Same','cards':[]},{'title':'Same','cards':[]}]});a,b=[v['id'] for v in d['views']];i=f.store.put_image('alice','One',png());j=f.store.put_image('alice','Two',png('blue'));value=defaults();value['roomImages']={a:i['id'],b:j['id']};d=save(f.store,'alice',d['id'],d['revision'],value)
  plan=get_plan(d);plan['views'].reverse();plan['views'][0].update(title='Renamed',visible=False);d=save_plan(f.store,'alice',d['id'],d['revision'],plan,[],{});self.assertEqual(d['design'],value)
  plan['views']=[v for v in plan['views'] if v['id']!=a]
  with self.assertRaises(Exception):save_plan(f.store,'alice',d['id'],d['revision'],plan,[],{})
  self.assertEqual(f.store.get('alice',d['id']),d)
  d=save_plan(f.store,'alice',d['id'],d['revision'],plan,[a],{});self.assertEqual(d['design']['roomImages'],{b:j['id']});self.assertEqual(inspect(f.store.path),2);self.assertEqual(len(f.store.images('alice')),2)
 def test_http_image_pipeline_formats_limits_metadata_and_owner_guards(self):
  import io
  from PIL import Image
  f=self.f;d=f.store.create('alice','Upload boundaries');before=copy.deepcopy(d);csrf=f.request('GET','/api/session')[1]['csrf']
  for fmt in ('PNG','JPEG','WEBP'):
   im=Image.new('RGB',(16,12),'#567890');exif=Image.Exif();exif[270]='Synthetic private metadata';b=io.BytesIO();im.save(b,fmt,exif=exif)
   body={'name':'Synthetic.'+fmt.lower(),'data':base64.b64encode(b.getvalue()).decode()};status,m=f.post('/api/images',body);self.assertEqual(status,201,m);status,raw=f.request('GET','/api/images/'+m['id']);self.assertEqual(status,200)
   with Image.open(io.BytesIO(raw)) as decoded:self.assertEqual(decoded.format,'PNG');self.assertFalse(decoded.getexif());self.assertNotIn('exif',decoded.info)
   self.assertEqual(f.request('GET','/api/images/'+m['id'],user='bob')[0],404)
  count=len(f.store.images('alice'))
  invalid=[b'<svg/>',png()[:32],png(size=(4097,1)),png(size=(3000,3000)),b'x'*(8*1024*1024+1)]
  for raw in invalid:
   with self.subTest(length=len(raw)):self.assertIn(f.post('/api/images',{'name':'Rejected','data':base64.b64encode(raw).decode()})[0],(413,422))
  body={'name':'No CSRF','data':base64.b64encode(png()).decode()};self.assertEqual(f.request('POST','/api/images',body)[0],403);self.assertEqual(f.request('POST','/api/images',body,extra={'X-LUMO-CSRF':csrf,'Origin':'https://evil.invalid'})[0],403);self.assertEqual(len(f.store.images('alice')),count);self.assertEqual(f.store.get('alice',d['id']),before)
 def test_binding_map_bounds_and_foreign_view_reject_without_revision_change(self):
  from design import defaults,save
  from store import StudioError
  f=self.f;d=f.store.import_native('alice','Map boundaries',{'views':[{'title':'View','cards':[]}]});other=f.store.import_native('alice','Other dashboard',{'views':[{'title':'View','cards':[]}]});image=f.store.put_image('alice','Image',png());base=defaults()
  for binding in ({other['views'][0]['id']:image['id']},{format(i,'032x'):image['id'] for i in range(257)},{'A'*32:image['id']}):
   value=copy.deepcopy(base);value['roomImages']=binding
   with self.assertRaises(StudioError):save(f.store,'alice',d['id'],d['revision'],value)
   self.assertEqual(f.store.get('alice',d['id']),d)
if __name__=='__main__':unittest.main()
