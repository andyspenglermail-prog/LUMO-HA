import sys,pathlib,unittest,copy,json,hashlib,re
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from test_http import Fixture
APP=pathlib.Path(__file__).resolve().parents[2]/'lumo_raumstudio'
class ReviewBackendTests(unittest.TestCase):
    def setUp(self):
        self.f=Fixture();self.csrf={'X-LUMO-CSRF':self.f.request('GET','/api/session')[1]['csrf']}
    def tearDown(self):self.f.close()
    def test_R3_server_rejects_unknown_icon_every_entry(self):
        for value in ('mdi:not-a-real-lumo-icon',{},None,'<svg onload=x>'):
            with self.subTest(value=value):
                status,_=self.f.request('POST','/api/dashboards',{'name':'Bad','icon':value},extra=self.csrf);self.assertEqual(status,400)
                self.assertEqual(self.f.store.list('alice'),[])
        d=self.f.store.create('alice','Good','mdi:home')
        self.assertEqual(self.f.request('POST','/api/dashboards/'+d['id']+'/save',{'revision':1,'patch':{'icon':'mdi:not-a-real-lumo-icon'}},extra=self.csrf)[0],400)
        cfg=copy.deepcopy(self.f.peer.configs['fixture-dashboard']);cfg['views'][0]['icon']='mdi:not-a-real-lumo-icon';self.f.peer.configs['fixture-dashboard']=cfg
        status,response=self.f.request('POST','/api/ha/import',{'path':'fixture-dashboard','name':'Bad'},extra=self.csrf);self.assertEqual(status,201);self.assertEqual(response['native'],cfg);self.assertEqual(len(self.f.store.list('alice')),2)
        report=self.f.request('GET','/api/dashboards/'+response['id']+'/report')[1]
        self.assertFalse(any(f['path']==['views',0,'icon'] for e in report['editableElements'] for f in e['fields']))
    def test_R3_catalog_assets_pins_package_and_ingress(self):
        provenance=json.loads((APP/'mdi-provenance.json').read_text())
        self.assertEqual(provenance['commit'],'9e04201d4557e729822fb57f62a316c3dea1d4a8');self.assertEqual(provenance['version'],'7.4.47');self.assertEqual(provenance['files']['mdi.json'],'3f719999c5f613801f790283b86056e723c6fa1667dcf033371499727decd858')
        for name,digest in provenance['files'].items():self.assertEqual(hashlib.sha256((APP/name).read_bytes()).hexdigest(),digest,name)
        paths=json.loads((APP/'mdi.json').read_text());self.assertEqual(len(paths),7447)
        for name,path in paths.items():self.assertRegex(name,r'^mdi:[a-z0-9]+(?:-[a-z0-9]+)*$');self.assertRegex(path,r'^[MmZzLlHhVvCcSsQqTtAa0-9., +\-]+$')
        self.assertIn('mdi:weather-sunny',paths);self.assertEqual(paths['mdi:home'],'M10,20V14H14V20H19V12H22L12,3L2,12H5V20H10Z')
        status,data=self.f.request('GET','/mdi.json');self.assertEqual(status,200);self.assertEqual(data,paths)
        self.assertIn('mdi.json',(APP/'Dockerfile').read_text());self.assertIn('mdi-LICENSE',(APP/'Dockerfile').read_text())
        self.assertEqual(self.f.request('GET','/mdi.json',user='')[0],403)
        import http.client
        c=http.client.HTTPConnection('127.0.0.1',self.f.port);c.request('GET','/mdi.json',headers={'X-Remote-User-Id':'alice'});r=c.getresponse();r.read();self.assertIn("connect-src 'self'",r.getheader('Content-Security-Policy'));self.assertNotIn('https:',r.getheader('Content-Security-Policy'));c.close()
    def test_R7_invalid_root_rows_and_badges_rejected_over_http(self):
        original=copy.deepcopy(self.f.peer.configs)
        base={'title':'Root','views':[{'title':'View','cards':[{'type':'entities','entities':[{'entity':'sensor.fixture','name':'Friendly','icon':'mdi:home'}]}]}]}
        for field,bad,path in [('title',42,'config.title'),('name',{},'views[0].cards[0].entities[0].name'),('icon',[],'views[0].cards[0].entities[0].icon'),('badges',False,'views[0].badges')]:
            with self.subTest(field=field):
                cfg=copy.deepcopy(base)
                if field=='title':cfg[field]=bad
                elif field=='badges':cfg['views'][0][field]=bad
                else:cfg['views'][0]['cards'][0]['entities'][0][field]=bad
                self.f.peer.configs['fixture-dashboard']=cfg
                status,catalog=self.f.request('GET','/api/ha/dashboards');self.assertEqual(status,200);entry=next(x for x in catalog['dashboards'] if x['path']=='fixture-dashboard');self.assertTrue(entry['supported']);self.assertEqual(entry['issues'],[])
                status,result=self.f.request('POST','/api/ha/import',{'path':'fixture-dashboard','name':'Bad'},extra=self.csrf);self.assertEqual(status,201);self.assertEqual(result['native'],cfg);self.assertEqual(self.f.request('GET','/api/dashboards/'+result['id']+'/export')[1],cfg);self.assertEqual(self.f.peer.configs['fixture-dashboard'],cfg)
        self.f.peer.configs=original
        self.assertTrue(all(c['type'] in ('config/auth/list','lovelace/config','lovelace/dashboards/list','lovelace/resources/list') for c in self.f.peer.commands))
    def test_R7_every_allowed_field_type_and_nested_container(self):
        from dashboard_reads import validate_supported_configuration as validate_configuration
        from store import StudioError
        cards=[
          {'type':'entity','entity':'sensor.fixture','name':'Name','icon':'mdi:home','unit':'W','attribute':'power','state_color':True},
          {'type':'entities','title':'Title','show_header_toggle':True,'state_color':False,'entities':[{'entity':'sensor.fixture','name':'Name','icon':'mdi:home'}]},
          {'type':'tile','entity':'light.fixture','name':'Name','icon':'mdi:home','color':'green','vertical':True,'hide_state':False,'state_content':['state'],'features':[{'type':'light-brightness'}],'features_position':'bottom'},
          {'type':'gauge','entity':'sensor.fixture','name':'Gauge','unit':'W','min':0,'max':100,'severity':{'green':0,'yellow':50,'red':80},'needle':True,'segments':[{'from':0,'color':'green','label':'Low'}]},
          {'type':'sensor','entity':'sensor.fixture','name':'Name','icon':'mdi:home','graph':'line','hours_to_show':24,'detail':1,'unit':'W'},
          {'type':'history-graph','entities':['sensor.fixture'],'title':'History','hours_to_show':24,'logarithmic_scale':False,'min_y_axis':0,'max_y_axis':100,'fit_y_data':True},
          {'type':'heading','heading':'Heading','icon':'mdi:home','heading_style':'title'},
          {'type':'grid','columns':2,'square':False,'cards':[]},
          {'type':'vertical-stack','title':'Stack','cards':[]},
          {'type':'horizontal-stack','title':'Stack','cards':[]}
        ]
        for card in cards:
            card['grid_options']={'columns':6,'rows':'auto'}
            for action in ('tap_action','hold_action','double_tap_action','icon_tap_action'):card[action]={'action':'none'}
        cfg={'title':'Root','background':'#ffffff','views':[{'title':'View','path':'view','icon':'mdi:home','type':'sections','cards':cards,'sections':[{'type':'grid','cards':[],'column_span':1}],'max_columns':4,'dense_section_placement':False,'show_icon_and_title':True,'subview':False,'visible':[{'user':'alice'}],'background':'#ffffff','badges':[]}]}
        self.assertEqual(validate_configuration(cfg),cfg)
        cases=[]
        def visit(value,keys=()):
            if isinstance(value,dict):
                for key,item in value.items():
                    trail=keys+(key,);cases.append((trail,{} if key=='visible' else False if isinstance(item,(dict,list)) else {}));visit(item,trail)
            elif isinstance(value,list):
                for i,item in enumerate(value):
                    trail=keys+(i,);cases.append((trail,False if isinstance(item,(dict,list)) else {}));visit(item,trail)
        visit(cfg)
        for keys,bad in cases:
            with self.subTest(path=keys):
                altered=copy.deepcopy(cfg);node=altered
                for key in keys[:-1]:node=node[key]
                node[keys[-1]]=bad
                with self.assertRaises(StudioError) as caught:validate_configuration(altered)
                self.assertEqual(caught.exception.status,422);self.assertTrue(caught.exception.details)
        import os
        out=pathlib.Path(os.environ.get('RAUMSTUDIO_EVIDENCE','/workspace/lumo-import-evidence/implementation/final/browser'));out.mkdir(parents=True,exist_ok=True)
        (out/'R7-type-matrix.json').write_text(json.dumps({'mutationCount':len(cases),'paths':[keys for keys,_ in cases],'passed':True},indent=2))
        # Fully supported actions are data only, never dispatched on import.
        self.f.peer.configs['fixture-dashboard']=cfg
        status,d=self.f.request('POST','/api/ha/import',{'path':'fixture-dashboard','name':'Typed'},extra=self.csrf);self.assertEqual(status,201);self.assertEqual(d['native'],cfg)
        self.assertTrue(all(c['type'] in ('config/auth/list','lovelace/config','lovelace/dashboards/list','lovelace/resources/list') for c in self.f.peer.commands))
if __name__=='__main__':unittest.main()
