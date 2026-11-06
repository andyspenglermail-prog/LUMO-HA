"""Step3 behavioral contracts against real HTTP, Store and CoreClient peer."""
import copy,json,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from test_rooms import RoomFixture

class DesignStoreTests(unittest.TestCase):
 def setUp(self): self.f=RoomFixture()
 def tearDown(self): self.f.close()
 def test_owner_cas_overlay_preserves_original_export_and_restart(self):
  f=self.f;d=f.store.import_native('alice','Design fixture',{'views':[{'title':'Original','cards':[{'type':'custom:protected','template':'[[[ forbidden() ]]]'}]}]})
  url='/api/dashboards/'+d['id']+'/design';status,r=f.request('GET',url)
  self.assertEqual(status,200,r)
  self.assertEqual(r['dashboardId'],d['id']);self.assertEqual(r['revision'],d['revision'])
  design=r['design'];design['profile']='ivory';design['overrides']={'radius':24}
  status,saved=f.post(url,{'revision':d['revision'],'design':design});self.assertEqual(status,200,saved)
  self.assertEqual(saved['design'],design)
  for key in ('native','nativeImport','views','settings'):self.assertEqual(saved[key],d[key])
  self.assertEqual(f.post(url,{'revision':d['revision'],'design':design})[0],409)
  self.assertEqual(f.request('GET',url,user='bob')[0],404)
  self.assertEqual(f.post(url,{'revision':saved['revision'],'design':design},user='bob')[0],404)
  from store import Store
  self.assertEqual(Store(f.store.path).get('alice',d['id']),saved)
  self.assertEqual(f.request('GET','/api/dashboards/'+d['id']+'/export')[1],d['native'])
 def test_closed_validation_catalog_and_contrast(self):
  f=self.f;d=f.store.create('alice','Validation');url='/api/dashboards/'+d['id']+'/design';r=f.request('GET',url)[1]
  self.assertIn('design',r,r)
  base=r['design']
  invalid=[('schemaVersion',True),('category','invented'),('profile','planned'),('targets',[]),('targets',['desktop','desktop']),('activeTarget','phone'),('options',{'highContrast':False,'motion':'script'}),('overrides',{'radius':True}),('overrides',{'text':'#ffffff','card':'#ffffff'}),('overrides',{'material':'url(evil)'}),('overrides',{'alien':1})]
  for key,value in invalid:
   v=copy.deepcopy(base);v[key]=value
   self.assertEqual(f.post(url,{'revision':1,'design':v})[0],400,(key,value))
  for field,value in [('width',True),('width',0),('width',8192),('height',-1),('dpr',9),('orientation','diagonal'),('diagonal',0),('hardwareWidth',True),('client','evil'),('kiosk',1)]:
   v=copy.deepcopy(base);v['displays']['desktop'][field]=value
   self.assertEqual(f.post(url,{'revision':1,'design':v})[0],400,(field,value))
  self.assertEqual(f.store.get('alice',d['id']),d)
  status,c=f.request('GET','/design-catalog.json');self.assertEqual(status,200)
  self.assertEqual(len(c['categories']),10);self.assertEqual(sum(len(x['profiles']) for x in c['categories']),30)
  self.assertEqual([p['id'] for x in c['categories'] for p in x['profiles'] if p['available']],['noir','ivory','smart'])
 def test_native_projection_background_priority_and_inert_custom_cards(self):
  f=self.f;native={'background':'#123456','views':[{'title':'Own','background':'#654321','cards':[{'type':'tile','entity':'light.fixture'},{'type':'custom:evil','entity':'sensor.fixture','name':'Protected template','javascript':'evil()'}]},{'title':'Inherited','cards':[]},{'title':'External','background':'url(https://invalid.example/x)','cards':[]}]};d=f.store.import_native('alice','Native',native);status,r=f.request('GET','/api/dashboards/'+d['id']+'/design');self.assertEqual(status,200)
  self.assertIn('sources',r);sources=r['sources'];self.assertEqual(sources[d['views'][0]['id']]['background'],{'value':'#654321','source':'Ansicht','supported':True});self.assertEqual(sources[d['views'][1]['id']]['background']['value'],'#123456');self.assertFalse(sources[d['views'][2]['id']]['background']['supported']);self.assertEqual(sources[d['views'][0]['id']]['refs'],[{'key':'state:light.fixture','entityId':'light.fixture'}]);self.assertEqual(sources[d['views'][0]['id']]['protected'][0]['type'],'custom:evil');self.assertEqual(f.store.get('alice',d['id']),d)
 def test_native_theme_sidecar_preserves_export(self):
  f=self.f;d=f.store.import_native('alice','Native',{'views':[{'title':'Original','cards':[]}]});base=f.request('GET','/api/dashboards/'+d['id']+'/design')[1]['design']
  for theme,radius in [('noir',16),('ivory',28),('smart',6)]:
   base['profile']=theme;d=f.post('/api/dashboards/'+d['id']+'/design',{'revision':d['revision'],'design':base})[1]
   status,r=f.request('GET','/api/dashboards/'+d['id']+'/design-native');self.assertEqual(status,200,r);self.assertEqual(r['revision'],d['revision']);self.assertEqual(r['themes'][r['themeName']]['ha-card-border-radius'],str(radius)+'px');self.assertFalse(r['changesOriginalExport']);self.assertIn('preview-only',[x['status'] for x in r['capabilities']]);self.assertEqual(f.request('GET','/api/dashboards/'+d['id']+'/export')[1],d['native'])
 def test_real_013_database_upgrade_backup_restore_and_raw_bytes(self):
  import subprocess,tempfile,tarfile,io,sqlite3,os
  from store import Store
  from maintenance import backup,restore
  f=self.f;root=pathlib.Path(__file__).resolve().parents[2];old=f.root/'actual-013';old.mkdir();raw=subprocess.check_output(['git','archive','af62301fa87a25d3992be32d0a395c81ed6a1138','lumo_raumstudio'],cwd=root)
  with tarfile.open(fileobj=io.BytesIO(raw)) as a:a.extractall(old,filter='data')
  db=f.root/'legacy.sqlite';script="import sys,io;sys.path.insert(0,sys.argv[1]);from store import Store;from PIL import Image;s=Store(sys.argv[2]);d=s.import_native('alice','Actual 013',{'views':[{'title':'Legacy','cards':[{'type':'custom:keep','number':9007199254740993}]}]});b=io.BytesIO();Image.new('RGB',(2,3),'red').save(b,'PNG');s.put_image('alice','legacy image',b.getvalue())"
  subprocess.run([sys.executable,'-B','-c',script,str(old/'lumo_raumstudio'),str(db)],check=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
  def byteset():
   with sqlite3.connect(db) as c:return c.execute('SELECT * FROM dashboards').fetchall(),c.execute('SELECT * FROM images').fetchall()
  before=byteset();s=Store(db);self.assertEqual(byteset(),before);d=s.list('alice')[0];from design import save,defaults
  updated=save(s,'alice',d['id'],d['revision'],defaults());snap=f.root/'backup.sqlite';backup(db,snap);s.update('alice',d['id'],updated['revision'],{'description':'temporary'});restore(snap,db);self.assertEqual(Store(db).get('alice',d['id']),updated);self.assertEqual(byteset()[1],before[1]);self.assertEqual(updated['native'],d['native']);self.assertFalse(list(old.rglob('*.pyc')))
 def test_new_routes_retain_csrf_origin_owner_and_options_revocation(self):
  f=self.f;d=f.store.create('alice','Security');url='/api/dashboards/'+d['id']+'/design';base=f.request('GET',url)[1]['design'];body={'revision':1,'design':base};csrf=f.request('GET','/api/session')[1]['csrf']
  self.assertEqual(f.request('POST',url,body)[0],403);self.assertEqual(f.request('POST',url,body,extra={'X-LUMO-CSRF':csrf,'Origin':'https://evil.invalid'})[0],403);self.assertEqual(f.request('GET',url+'-native',user='bob')[0],404);f.options.write_text(json.dumps({'enabled':False,'allowed_user_ids':[]}));self.assertEqual(f.request('POST',url,body,extra={'X-LUMO-CSRF':csrf})[0],403);self.assertEqual(f.request('GET',url)[0],403);self.assertEqual(f.store.get('alice',d['id']),d)
if __name__=='__main__':unittest.main()
