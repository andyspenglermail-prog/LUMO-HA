import copy,pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from test_rooms import RoomFixture
from design import CATALOG,defaults,validate,resolved,contrast
from store import Store,StudioError
from maintenance import backup,restore
class ReferenceDesignTests(unittest.TestCase):
 def setUp(self):self.f=RoomFixture()
 def tearDown(self):self.f.close()
 def test_reversible_dark_icon_glass_sidecar_validation(self):
  f=self.f;d=f.store.create('alice','Variants');url='/api/dashboards/'+d['id']+'/design';value=defaults();value['options'].update(darkMode=True,iconStyle='linear');value['overrides']['material']='glass';value['overrides']['radius']=23
  status,saved=f.post(url,{'revision':1,'design':value});self.assertEqual(status,200,saved)
  for profile in ('noir','ivory','smart'):
   value['profile']=profile;self.assertGreaterEqual(contrast(resolved(value)['text'],resolved(value)['card']),4.5)
   self.assertNotEqual(resolved(value)['card'],CATALOG['profiles'][profile]['card']);value['options']['darkMode']=False;self.assertEqual(resolved(value)['card'],CATALOG['profiles'][profile]['card']);value['options']['darkMode']=True
  for key,bad in [('darkMode',None),('darkMode',1),('darkMode','true'),('iconStyle',None),('iconStyle',False),('iconStyle','emoji')]:
   v=copy.deepcopy(value);v['options'][key]=bad;self.assertEqual(f.post(url,{'revision':saved['revision'],'design':v})[0],400)
  report=f.request('GET',url+'-native')[1];self.assertIn('preview-only',[x['status'] for x in report['capabilities'] if 'Glas' in x['feature']]);self.assertNotIn('blur',report['themes'][report['themeName']]['ha-card-background']);self.assertEqual(saved['settings'],d['settings'])
 def test_dashboard_favorites_strict_validation_guards_backup_legacy(self):
  f=self.f;d=f.store.import_native('alice','Favorites',{'views':[{'title':'Opaque','cards':[{'type':'custom:keep','n':9007199254740993}]}]});url='/api/dashboards/'+d['id']+'/design';value=defaults();ids=[p['id'] for c in CATALOG['categories'] for p in c['profiles']];value['favorites']=ids
  status,saved=f.post(url,{'revision':d['revision'],'design':value});self.assertEqual(status,200,saved);self.assertEqual(saved['design']['favorites'],ids)
  self.assertEqual(f.post(url,{'revision':d['revision'],'design':value})[0],409);self.assertEqual(f.post(url,{'revision':saved['revision'],'design':value},user='bob')[0],404);self.assertEqual(f.request('POST',url,{'revision':saved['revision'],'design':value})[0],403)
  for bad in [None,True,False,1,10**100,float('nan'),{},['unknown'],['noir','noir'],[None],[True],[10**100],[float('nan')],ids+['noir']]:
   with self.subTest(bad=repr(bad)):
    v=copy.deepcopy(value);v['favorites']=bad;self.assertEqual(f.post(url,{'revision':saved['revision'],'design':v})[0],400);self.assertEqual(f.store.get('alice',d['id']),saved)
  for k in ('native','nativeImport','views','settings'):self.assertEqual(saved[k],d[k])
  snap=f.root/'fav.sqlite';backup(f.store.path,snap);f.store.update('alice',d['id'],saved['revision'],{'name':'Temporary'});restore(snap,f.store.path);self.assertEqual(Store(f.store.path).get('alice',d['id']),saved)
  legacy=defaults();self.assertNotIn('favorites',legacy);self.assertEqual(validate(legacy),legacy)
