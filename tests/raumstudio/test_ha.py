import sys,pathlib,unittest,copy
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'lumo_raumstudio'))
from peer import Peer,CONFIG
from client import CoreClient
from dashboard_reads import DashboardReads
class HATests(unittest.TestCase):
    def setUp(self):self.peer=Peer();self.api=DashboardReads(CoreClient('synthetic-test-token',host='127.0.0.1',port=self.peer.server.server_address[1]))
    def tearDown(self):self.peer.close()
    def test_verified_admin_catalog_and_atomic_native_import(self):
        rows=self.api.catalog('alice');self.assertEqual(len(rows),3,'Real websocket catalogue plus verified default config')
        self.assertEqual(rows[0]['viewCount'],1)
        before=copy.deepcopy(self.peer.configs)
        result=self.api.read('alice','fixture-dashboard');self.assertEqual(result['config'],CONFIG)
        with self.assertRaises(Exception) as error:self.api.read('alice','bad-dashboard')
        self.assertIn('views[0].cards[0]',str(error.exception))
        self.assertEqual(self.peer.configs,before)
        self.assertTrue(set(c['type'] for c in self.peer.commands)<={'config/auth/list','lovelace/dashboards/list','lovelace/config'})
    def test_nonadmin_or_inactive_cannot_read(self):
        with self.assertRaises(Exception):self.api.catalog('bob')
        self.assertEqual([c['type'] for c in self.peer.commands],['config/auth/list'])
        self.peer.users[0]['is_active']=False
        with self.assertRaises(Exception):self.api.catalog('alice')
    def test_native_known_fields_are_typed_not_opaque(self):
        from dashboard_reads import validate_configuration
        from store import StudioError
        for card in [
            {'type':'tile','entity':'sensor.synthetic','grid_options':{'columns':['invalid'],'rows':1}},
            {'type':'gauge','entity':'sensor.synthetic','min':100,'max':0},
            {'type':'entities','entities':['sensor.synthetic'],'show_header_toggle':'yes'},
            {'type':'tile','entity':'sensor.synthetic','features':[{'type':'light-brightness','evil':True}]}]:
            with self.subTest(card=card):
                with self.assertRaises(StudioError) as e:validate_configuration({'views':[{'title':'Test','cards':[card]}]})
                self.assertIn('views[0].cards[0]',str(e.exception))
    def test_sections_copy_preserves_tiles_and_rejects_mixed_partial(self):
        native={'title':'Native Sections','views':[{'title':'Vorhanden','path':'vorhanden','type':'sections','max_columns':3,'sections':[{'type':'grid','cards':[{'type':'heading','heading':'Gruppe'},{'type':'tile','entity':'light.synthetic','name':'Vorhandene Kachel','grid_options':{'columns':6,'rows':2},'features':[{'type':'light-brightness'}],'tap_action':{'action':'none'},'icon_tap_action':{'action':'none'}},{'type':'gauge','entity':'sensor.synthetic','min':0,'max':100}]}]}]}
        self.peer.configs['fixture-dashboard']=copy.deepcopy(native)
        self.assertEqual(self.api.read('alice','fixture-dashboard')['config'],native)
        self.peer.configs['fixture-dashboard']['views'][0]['sections'][0]['cards'].append({'type':'custom:missing'})
        with self.assertRaises(Exception) as e:self.api.read('alice','fixture-dashboard')
        self.assertIn('views[0].sections[0].cards[3].type',str(e.exception))
        self.peer.configs[None]=None
        rows=self.api.catalog('alice');self.assertTrue(all(r['path'] is not None for r in rows))
        self.peer.configs['fixture-dashboard']={'strategy':{'type':'original-states'}}
        rows=self.api.catalog('alice');entry=next(r for r in rows if r['path']=='fixture-dashboard');self.assertIsNone(entry['viewCount']);self.assertFalse(entry['supported'])
if __name__=='__main__':unittest.main()
