import sys,pathlib,tempfile,unittest,json,threading,copy
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'lumo_raumstudio'))
from test_http import Fixture
from room_peer import RoomPeer
from store import Store
from policy import load_snapshot
from server import create_server
from client import CoreClient
class RoomFixture(Fixture):
 def __init__(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name);self.options=self.root/'options.json';self.options.write_text(json.dumps({'enabled':True,'allowed_user_ids':['alice','bob','admin']}));self.store=Store(self.root/'studio.sqlite');self.peer=RoomPeer();self.trusted='127.0.0.1';self.start()
 def post(self,path,value,user='alice'):
  csrf=self.request('GET','/api/session',user=user)[1]['csrf'];return self.request('POST',path,value,user=user,extra={'X-LUMO-CSRF':csrf})
class InventoryTests(unittest.TestCase):
 def setUp(self):self.f=RoomFixture()
 def tearDown(self):self.f.close()
 def test_runtime_inventory_identity_precedence_and_complete_states(self):
  status,r=self.f.request('GET','/api/ha/inventory');self.assertEqual(status,200,r)
  self.assertEqual(len(r['areas']),2);self.assertEqual(len(r['floors']),1);self.assertEqual(len(r['devices']),2);self.assertEqual(len(r['entities']),5)
  e={x['key']:x for x in r['entities']}
  self.assertEqual((e['registry:reg1']['effectiveAreaId'],e['registry:reg1']['areaSource']),('a','device'))
  self.assertEqual((e['registry:reg2']['effectiveAreaId'],e['registry:reg2']['areaSource']),('b','entity'))
  self.assertEqual(e['registry:reg1']['attributes']['brightness'],128)
  self.assertEqual(e['registry:reg3']['availability'],'disabled');self.assertEqual(e['registry:reg2']['availability'],'unavailable');self.assertEqual(e['registry:reg4']['availability'],'unknown')
  self.assertEqual(e['state:weather.state_only']['areaSource'],'none');self.assertIsNone(e['state:weather.state_only']['registryId'])
  self.assertEqual(r['areas'][0]['entityCount'],2);self.assertEqual(r['areas'][1]['entityCount'],1)
  self.assertTrue(r['fetchedAt']);self.assertEqual(r['status'],'fresh');self.assertFalse(r['canCorrect']);self.assertEqual(r['version'],'2026.11.0')
  self.assertNotIn('config/auth/list',[c['type'] for c in self.f.peer.commands])
  self.f.peer.data['entities'][0]['entity_id']='light.renamed';self.f.peer.data['states'][0]['entity_id']='light.renamed';self.f.peer.data['states'][0]['state']='off'
  latest=self.f.request('GET','/api/ha/inventory')[1];renamed=next(x for x in latest['entities'] if x['key']=='registry:reg1');self.assertEqual(renamed['entityId'],'light.renamed');self.assertEqual(renamed['state'],'off')
 def test_different_token_user_requires_requester_admin(self):
  self.assertEqual(self.f.request('GET','/api/ha/inventory',user='bob')[0],403)
  self.assertEqual(self.f.request('GET','/api/ha/inventory',user='admin')[0],200)
  self.f.peer.identity={'id':'supervisor','is_admin':True,'is_owner':True}
  before=len(self.f.peer.commands);self.assertEqual(self.f.request('GET','/api/ha/inventory',user='bob')[0],403)
  self.assertFalse(any(c['type'].endswith('registry/list') for c in self.f.peer.commands[before:]))
 def test_read_failure_does_not_return_fake_or_cached_fresh_inventory(self):
  self.assertEqual(self.f.request('GET','/api/ha/inventory')[0],200);self.f.peer.fail='get_states';status,r=self.f.request('GET','/api/ha/inventory');self.assertEqual(status,502);self.assertNotIn('entities',r)
if __name__=='__main__':unittest.main()
