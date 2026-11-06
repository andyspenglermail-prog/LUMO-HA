import sys,pathlib,unittest,copy,sqlite3,subprocess,json,io
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'lumo_raumstudio'))
from test_rooms import RoomFixture
from store import Store
from maintenance import backup,restore
from native import compile_native
from PIL import Image
from contextlib import closing
import tarfile
def rows(path,sql):
 with closing(sqlite3.connect(path)) as c:return c.execute(sql).fetchall()

def view(id='1'*32,title='Virtuell',area=None):
 return {'id':id,'title':title,'icon':'mdi:home','visible':True,'areaId':area,'source':'ha-area' if area else 'virtual','nativeViewId':None,'deviceIds':['dev'],'entityRefs':[{'key':'registry:reg1','entityId':'light.fixture'},{'key':'registry:reg2','entityId':'sensor.fixture'}]}
class RoomStoreTests(unittest.TestCase):
 def setUp(self):self.f=RoomFixture();self.d=self.f.store.create('alice','Fixture Dashboard');self.path='/api/dashboards/'+self.d['id']+'/rooms'
 def tearDown(self):self.f.close()
 def save(self,views,revision=None,confirmed=None,user='alice'):
  return self.f.post(self.path,{'revision':revision or self.d['revision'],'plan':{'schemaVersion':1,'views':views},'confirmedDeletes':confirmed or []},user)
 def test_room_lifecycle_cas_owner_and_restart_backup(self):
  status,r=self.save([view()]);self.assertEqual(status,200,r);self.d=r;self.assertEqual(r['roomPlan']['views'][0]['deviceIds'],['dev'])
  v=copy.deepcopy(r['roomPlan']['views'][0]);v.update(title='Neuer Name',icon='mdi:sofa',visible=False);duplicate=copy.deepcopy(v);duplicate['id']='2'*32
  status,r=self.save([duplicate,v]);self.assertEqual(status,200,r);self.d=r;self.assertEqual([x['id'] for x in r['roomPlan']['views']],['2'*32,'1'*32])
  self.assertEqual(self.save([v],revision=1)[0],409);self.assertEqual(self.save([v],user='bob')[0],404)
  self.assertEqual(self.save([v])[0],400);status,r=self.save([v],confirmed=['2'*32]);self.assertEqual(status,200,r);self.d=r
  self.f.stop();backup(self.f.store.path,self.f.root/'backup.sqlite');self.f.store=Store(self.f.store.path);self.f.start();self.assertEqual(self.f.request('GET',self.path)[1]['plan']['views'],[v]);self.assertEqual(self.f.request('GET','/api/dashboards/'+r['id'])[1],r)
  self.assertEqual(rows(self.f.store.path,'pragma user_version')[0][0],2)
 def test_native_overlay_never_changes_native_export_or_views(self):
  native={'views':[{'title':'Original','icon':'custom:untrusted','cards':[{'type':'custom:unknown','entity':'light.fixture','private':{'__proto__':[True,9007199254740993]}}]}],'unknown':{'template':'[[[return evil()]]]'}}
  d=self.f.store.import_native('alice','Native',native);self.path='/api/dashboards/'+d['id']+'/rooms';self.d=d
  status,r=self.f.request('GET',self.path);self.assertEqual(status,200,r);v=r['plan']['views'][0];self.assertEqual(v['nativeViewId'],d['views'][0]['id']);self.assertEqual(v['source'],'native');v['title']='Lokaler Titel';v['entityRefs']=[{'key':'registry:reg1','entityId':'light.fixture'}]
  status,r=self.save([v]);self.assertEqual(status,200,r);self.assertEqual(r['views'],d['views']);self.assertEqual(compile_native(self.f.store,'alice',r),native)
  self.f.store=Store(self.f.store.path);self.assertEqual(self.f.store.get('alice',d['id']),r)
 def test_rename_resolves_stable_refs_missing_preserved_invalid_rejected(self):
  self.f.peer.data['entities'][0]['entity_id']='light.renamed';self.f.peer.data['states'][0]['entity_id']='light.renamed'
  status,r=self.save([view()]);self.assertEqual(status,200,r);self.assertEqual(r['roomPlan']['views'][0]['entityRefs'][0],{'key':'registry:reg1','entityId':'light.renamed'});self.d=r
  self.f.peer.data['entities']=self.f.peer.data['entities'][1:]
  status,r=self.save(r['roomPlan']['views']);self.assertEqual(status,200,r);self.assertEqual(r['roomPlan']['views'][0]['entityRefs'][0]['key'],'registry:reg1');self.d=r
  for mutate in (lambda v:v.update(visible='true'),lambda v:v.update(id='bad'),lambda v:v.update(deviceIds=['dev','dev']),lambda v:v.update(unknown=True),lambda v:v.update(entityRefs=[{'key':'registry:invented','entityId':'light.fake'}])):
   v=view();mutate(v);self.assertEqual(self.save([v])[0],400)
 def test_local_virtual_save_survives_disconnected_or_unverifiable_ha(self):
  v=view();v['deviceIds']=[];v['entityRefs']=[];self.f.peer.fail='auth/current_user'
  status,r=self.save([v]);self.assertEqual(status,200,r);self.d=r;self.f.peer.fail=None;self.f.peer.identity={'id':'supervisor','is_admin':True};self.f.peer.admins=[];v['title']='Ohne HA-Rechte lokal bearbeiten';status,r=self.save([v]);self.assertEqual(status,200,r)
 def test_true_baseline_database_load_preserves_lossless_and_image_bytes(self):
  # Run the actual immutable released Store, not a hand-made new-schema approximation.
  old=self.f.root/'baseline.sqlite';script="import sys,io,json;sys.path.insert(0,sys.argv[1]);from store import Store;from PIL import Image;s=Store(sys.argv[2]);d=s.import_native('alice','Baseline',{'views':[{'title':'Alt','cards':[{'type':'custom:opaque','n':9007199254740993}]}],'opaque':[True,1,1.0]});b=io.BytesIO();Image.new('RGB',(3,2),'red').save(b,'PNG');s.put_image('alice','Altbild',b.getvalue())"
  baseline=self.f.root/'released';baseline.mkdir();archive=subprocess.check_output(['git','archive','--format=tar','ee27ba0dbf28269a0cf25ebee67006c32e8913bc','lumo_raumstudio'],cwd=pathlib.Path(__file__).resolve().parents[2])
  with tarfile.open(fileobj=io.BytesIO(archive)) as source:source.extractall(baseline,filter='data')
  subprocess.run([sys.executable,'-I','-B','-c',script,str(baseline/'lumo_raumstudio'),str(old)],check=True)
  before=rows(old,'select document from dashboards');image=rows(old,'select bytes from images');new=Store(old)
  self.assertEqual(rows(old,'select document from dashboards'),before);self.assertEqual(rows(old,'select bytes from images'),image)
  from room_store import get_plan
  self.assertEqual(len(get_plan(new.list('alice')[0])['views']),1);backup(old,self.f.root/'oldbackup.sqlite');restore(self.f.root/'oldbackup.sqlite',old);self.assertEqual(rows(old,'select document from dashboards'),before)
if __name__=='__main__':unittest.main()
