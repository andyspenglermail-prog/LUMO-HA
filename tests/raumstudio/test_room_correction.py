import sys,pathlib,unittest,copy
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'lumo_raumstudio'))
from test_rooms import RoomFixture
class CorrectionTests(unittest.TestCase):
 def setUp(self):self.f=RoomFixture();self.d=self.f.store.create('admin','Admin Fixture');self.base='/api/dashboards/'+self.d['id']+'/area-correction'
 def tearDown(self):self.f.close()
 def preview(self,kind='entity',target='reg1',area='b',user='admin'):
  return self.f.post(self.base+'/preview',{'revision':self.d['revision'],'kind':kind,'targetId':target,'areaId':area},user)
 def confirm(self,p,user='admin',confirm=True):return self.f.post(self.base+'/confirm',{'previewId':p['previewId'],'confirm':confirm},user)
 def writes(self):return [x for x in self.f.peer.commands if x['type'].endswith('/update')]
 def test_exact_preview_explicit_confirm_write_fresh_readback_single_use(self):
  status,p=self.preview();self.assertEqual(status,200,p);self.assertEqual(p['beforeAreaId'],None);self.assertEqual(p['afterAreaId'],'b');self.assertEqual(p['entityId'],'light.fixture');self.assertEqual(self.writes(),[])
  self.assertEqual(self.confirm(p,confirm=False)[0],400);status,p=self.preview();status,r=self.confirm(p);self.assertEqual(status,200,r);self.assertEqual(r['status'],'confirmed');self.assertEqual(r['actualAreaId'],'b');self.assertEqual(len(self.writes()),1);self.assertEqual(self.writes()[0]['entity_id'],'light.fixture');self.assertEqual(self.confirm(p)[0],409)
  status,p=self.preview('device','dev',None);self.assertEqual(status,200,p);self.assertGreater(len(p['affectedEntityIds']),0);self.assertEqual(self.confirm(p)[0],200);self.assertEqual(len(self.writes()),2)
 def test_nonadmin_fails_before_dispatch_and_supervisor_is_not_requester(self):
  self.d=self.f.store.create('alice','Nonadmin');self.base='/api/dashboards/'+self.d['id']+'/area-correction';self.assertEqual(self.preview(user='alice')[0],403)
  self.f.peer.identity={'id':'supervisor','is_admin':True};self.assertEqual(self.preview(user='alice')[0],403);self.assertEqual(self.writes(),[])
 def test_stale_object_area_dashboard_or_lost_rights_is_not_dispatched(self):
  status,p=self.preview();self.assertEqual(status,200,p);self.f.peer.data['entities'][0]['entity_id']='light.renamed';self.assertEqual(self.confirm(p)[0],409)
  status,p=self.preview();self.f.peer.data['areas'][1]['name']='Renamed target';self.assertEqual(self.confirm(p)[0],409)
  status,p=self.preview();self.f.store.update('admin',self.d['id'],self.d['revision'],{'name':'Other tab'});self.assertEqual(self.confirm(p)[0],409)
  self.d=self.f.store.get('admin',self.d['id']);status,p=self.preview();self.f.peer.admins=[];self.assertEqual(self.confirm(p)[0],403);self.assertEqual(self.writes(),[])
 def test_uncertain_write_and_mismatch_never_retry_or_claim_success(self):
  status,p=self.preview();self.assertEqual(status,200,p);self.f.peer.drop_write=True;status,r=self.confirm(p);self.assertEqual(status,502,r);self.assertIn('unklar',r['error']);self.assertEqual(len(self.writes()),1);self.assertEqual(self.confirm(p)[0],409)
  self.f.peer.drop_write=False;self.f.peer.ignore_write=True;status,p=self.preview(area='a');self.assertEqual(status,200,p);status,r=self.confirm(p);self.assertEqual(status,502,r);self.assertIn('unklar',r['error']);self.assertEqual(len(self.writes()),2)
 def test_expiration_during_fresh_preflight_never_dispatches(self):
  from area_corrections import AreaCorrections
  from rooms import RoomReads
  from client import CoreClient
  from store import StudioError
  from unittest.mock import patch
  reads=RoomReads(CoreClient('synthetic-test-token',host='127.0.0.1',port=self.f.peer.server.server_address[1]));writer=AreaCorrections(reads,self.f.store)
  p=writer.preview('admin',self.d['id'],{'revision':1,'kind':'entity','targetId':'reg1','areaId':'b'},lambda:None)
  # Only the monotonic clock is injected; the preflight uses the real WS peer.
  with patch('area_corrections.time.monotonic',side_effect=[writer.pending[p['previewId']]['expires']-1]+[writer.pending[p['previewId']]['expires']+1]*10000):
   with self.assertRaises(StudioError) as error:writer.confirm('admin',self.d['id'],{'previewId':p['previewId'],'confirm':True},lambda:None)
  self.assertEqual(error.exception.status,409);self.assertEqual(self.writes(),[])
 def test_invalid_target_scope_csrf_and_arbitrary_actions_denied(self):
  for kind,target,area in [('floor','f','a'),('entity','state:weather.state_only','a'),('device','absent','a'),('device','dev','missing')]:self.assertIn(self.preview(kind,target,area)[0],(400,404))
  self.assertEqual(self.f.request('POST',self.base+'/preview',{'kind':'device'})[0],403)
  self.assertEqual(self.f.post('/api/ha/call_service',{'domain':'light','service':'turn_on'},'admin')[0],404);self.assertEqual(self.writes(),[])
if __name__=='__main__':unittest.main()
