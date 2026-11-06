"""Public synthetic fixtures only: never use household snapshots here."""
import copy,json,pathlib,sys,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'lumo_raumstudio'))
from store import Store,StudioError
from native import compile_native

CONFIG={
    'title':'Native identity',
    'background':'center / cover url("https://external.invalid/background.png")',
    'button_card_templates':{'opaque':{'styles':{'card':['color: red']},'custom_fields':{'code':'[[[ window.__EXECUTED__ = true; return "x"; ]]]'}}},
    '__proto__':{'polluted':True},'constructor':{'prototype':{'polluted':True}},
    'unknown':{'null':None,'bool':False,'number':9007199254740993,'float':1.25,'list':[3,1,2]},
    'views':[
        {'title':'First','path':'first','background':{'image':'https://external.invalid/image.png'},'cards':[
            {'type':'custom:button-card','template':'opaque','card_mod':{'style':'ha-card {background: url(https://external.invalid/style)}'},'unknown':{'nested':[False,None,{'x':'<script>window.__EXECUTED__=true</script>'}]}},
            {'type':'vertical-stack','cards':[{'type':'entity','entity':'sensor.synthetic','name':'Known','card_mod':{'style':'/* protected */'}}]}]},
        {'title':'Second','path':'second','show_icon_and_title':False,'cards':[]}
    ]
}
class LosslessTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.s=Store(pathlib.Path(self.tmp.name)/'store.sqlite')
    def tearDown(self):self.tmp.cleanup()
    def test_opaque_import_persistence_export_and_management_overlay(self):
        source=copy.deepcopy(CONFIG)
        try:d=self.s.import_native('alice','Independent name',source)
        except StudioError as e:self.fail('Finite opaque HA JSON must be imported, not rejected: '+str(e))
        source['views'].reverse()
        self.assertEqual(d['native'],CONFIG)
        self.assertEqual(compile_native(self.s,'alice',d),CONFIG)
        settings=copy.deepcopy(d['settings']);settings['background']['color']='#112233';settings['navigation']['startView']=d['views'][1]['id']
        d=self.s.update('alice',d['id'],d['revision'],{'name':'Management only','settings':settings})
        reopened=Store(self.s.path).get('alice',d['id'])
        self.assertEqual(compile_native(self.s,'alice',reopened),CONFIG)
        clone=self.s.duplicate('alice',d['id'],d['revision'])
        self.assertEqual(compile_native(self.s,'alice',clone),CONFIG)
        self.s.delete('alice',clone['id'],clone['revision'],True)
        self.assertEqual(self.s.get('alice',d['id'])['native'],CONFIG)

    def test_backup_refuses_inconsistent_import_marker_and_edit_ledger(self):
        from maintenance import inspect
        d=self.s.import_native('alice','Backup integrity',CONFIG)
        corruptions=[]
        missing=copy.deepcopy(d);missing['native']=None;missing['views']=[];corruptions.append(missing)
        duplicate=copy.deepcopy(d);duplicate['views'][1]['id']=duplicate['views'][0]['id'];corruptions.append(duplicate)
        protected=copy.deepcopy(d);protected['nativeImport']['edits']=[{'path':['background'],'value':'tamper'}];corruptions.append(protected)
        for i,bad in enumerate(corruptions):
            with self.subTest(case=i):
                with self.s.connect() as c:c.execute('UPDATE dashboards SET document=? WHERE id=?',(json.dumps(bad),d['id']))
                with self.assertRaises((StudioError,ValueError)):inspect(self.s.path)
        with self.s.connect() as c:c.execute('UPDATE dashboards SET document=? WHERE id=?',(json.dumps(d),d['id']))
        self.assertEqual(inspect(self.s.path),2)

    def test_large_opaque_keys_do_not_amplify_report_or_export(self):
        from imported import report
        cfg={'k'*100000:[None]*200,'views':[]}
        d=self.s.import_native('alice','Large opaque key',cfg)
        summary=report(d)
        self.assertLess(len(json.dumps(summary)),1048576,'Diagnostic paths must not repeat unbounded opaque key text')
        self.assertTrue(any(x.get('pathTruncated') for x in summary['protected']['details']))
        self.assertEqual(compile_native(self.s,'alice',d),cfg)

    def test_legacy_envelope_keeps_its_original_validation_and_mapping(self):
        from peer import CONFIG as LEGACY
        from maintenance import inspect
        d=self.s.import_native('alice','Legacy management',LEGACY);d.pop('nativeImport')
        with self.s.connect() as c:c.execute('UPDATE dashboards SET document=? WHERE id=?',(json.dumps(d),d['id']))
        self.assertEqual(Store(self.s.path).get('alice',d['id']),d)
        self.assertEqual(compile_native(self.s,'alice',d)['title'],'Legacy management')
        d['native']['unsupported_corruption']=True
        with self.s.connect() as c:c.execute('UPDATE dashboards SET document=? WHERE id=?',(json.dumps(d),d['id']))
        with self.assertRaises((StudioError,ValueError)):inspect(self.s.path)

    def test_finite_bounds_are_not_supported_grammar(self):
        from dashboard_reads import validate_configuration,bounded
        source={'strategy':{'type':[]},'title':42,'views':[None,False,{'type':{},'title':{'opaque':True},'cards':[]}],'escaped':'\ud800','nested':{}}
        node=source['nested']
        for _ in range(35):node['next']={};node=node['next']
        try:d=self.s.import_native('alice','Opaque shapes',source)
        except Exception as e:self.fail('Bounded opaque JSON must survive independently of supported shape: '+type(e).__name__)
        self.assertEqual(compile_native(self.s,'alice',d),source)
        self.assertEqual(Store(self.s.path).get('alice',d['id'])['native'],source)
        for bad in [{'x':float('nan')},{'x':float('inf')},{'x':set()},['not-root-object'],{'x':'a'*1048577}]:
            with self.subTest(kind=type(bad).__name__):
                with self.assertRaises(StudioError):validate_configuration(bad)
        deep={};n=deep
        for _ in range(70):n['next']={};n=n['next']
        with self.assertRaises(StudioError):bounded(deep)

class LosslessHTTPTests(unittest.TestCase):
    def setUp(self):
        from test_http import Fixture
        self.f=Fixture();self.f.peer.configs['fixture-dashboard']=copy.deepcopy(CONFIG)
        self.headers={'X-LUMO-CSRF':self.f.request('GET','/api/session')[1]['csrf']}
    def tearDown(self):self.f.close()
    def request(self,method,path,value=None,**kw):return self.f.request(method,path,value,extra=self.headers,**kw)
    def imported(self):
        status,d=self.request('POST','/api/ha/import',{'path':'fixture-dashboard','name':'Independent'})
        self.assertEqual(status,201);return d
    def test_report_resource_snapshot_and_targeted_edit(self):
        d=self.imported();base='/api/dashboards/'+d['id']
        status,report=self.request('GET',base+'/report')
        self.assertEqual(status,200,'Import detail must expose a safe report, not reject custom JSON')
        self.assertEqual(report['resources']['status'],'captured')
        self.assertEqual(report['resources']['items'],self.f.peer.resources)
        self.assertEqual(report['resources']['verification'],'unverified')
        self.assertIn('custom:button-card',report['dependencies']['customCardTypes'])
        self.assertTrue(report['dependencies']['templates']);self.assertTrue(report['dependencies']['styles'])
        path=['views',0,'cards',1,'cards',0,'name']
        self.assertTrue(any(field['path']==path for e in report['editableElements'] for field in e['fields']))
        self.assertEqual(self.request('GET',base+'/export')[1],CONFIG)
        status,edited=self.request('POST',base+'/native-edit',{'revision':d['revision'],'edits':[{'path':path,'value':'Deliberately changed'}]})
        self.assertEqual(status,200,edited)
        self.assertEqual(edited['native'],CONFIG,'Server-held source cannot be overwritten')
        expected=copy.deepcopy(CONFIG);expected['views'][0]['cards'][1]['cards'][0]['name']='Deliberately changed'
        self.assertEqual(self.request('GET',base+'/export')[1],expected)
        self.assertEqual(self.f.store.get('alice',d['id']),edited)
        from maintenance import backup,restore
        snap=self.f.root/'backup.sqlite';backup(self.f.store.path,snap)
        restored=self.f.root/'restored.sqlite';Store(restored);restore(snap,restored)
        self.assertEqual(compile_native(Store(restored),'alice',Store(restored).get('alice',d['id'])),expected)
        self.assertEqual(self.f.peer.configs['fixture-dashboard'],CONFIG)
        self.assertTrue(set(c['type'] for c in self.f.peer.commands)<={'config/auth/list','lovelace/config','lovelace/resources/list'})
    def test_missing_resources_are_unknown_and_strategy_is_preserved(self):
        self.f.peer.resources=None
        source={'strategy':{'type':'custom:unknown','config':{'__proto__':{'x':False}}}}
        self.f.peer.configs['fixture-dashboard']=source
        d=self.imported();base='/api/dashboards/'+d['id']
        self.assertEqual(d['views'],[])
        status,report=self.request('GET',base+'/report');self.assertEqual(status,200)
        self.assertEqual(report['resources']['status'],'unavailable');self.assertIsNone(report['resources']['items'])
        self.assertEqual(self.request('GET',base+'/export')[1],source)
    def test_opaque_strings_and_default_catalog_label_survive_http(self):
        cfg={'title':42,'views':[{'title':'\ud800','cards':[]}],'unknown':'\udfff'}
        self.f.peer.configs['fixture-dashboard']=copy.deepcopy(cfg);self.f.peer.configs[None]=copy.deepcopy(cfg)
        status,rows=self.request('GET','/api/ha/dashboards');self.assertEqual(status,200)
        self.assertIsInstance(rows['dashboards'][0]['title'],str,'Display fallback must not modify opaque native title')
        d=self.imported();self.assertEqual(self.request('GET','/api/dashboards/'+d['id']+'/export')[1],cfg)
        self.assertEqual(self.request('GET','/api/dashboards/'+d['id'])[1]['native'],cfg)

    def test_protected_tamper_owner_cas_and_csrf_fail_closed(self):
        d=self.imported();base='/api/dashboards/'+d['id']
        good={'revision':1,'edits':[{'path':['title'],'value':'Explicit native title'}]}
        self.assertEqual(self.request('POST',base+'/native-edit',good)[0],200)
        self.assertEqual(self.request('POST',base+'/native-edit',good)[0],409)
        self.assertEqual(self.request('GET',base+'/export',user='bob')[0],404)
        self.assertEqual(self.request('GET',base+'/report',user='bob')[0],404)
        bob={'X-LUMO-CSRF':self.f.request('GET','/api/session',user='bob')[1]['csrf']}
        self.assertEqual(self.f.request('POST',base+'/native-edit',dict(good,revision=2),user='bob',extra=bob)[0],404)
        self.assertEqual(self.f.request('POST',base+'/native-edit',dict(good,revision=2))[0],403)
        before=self.f.store.get('alice',d['id'])
        for path in [['__proto__','polluted'],['background'],['views',0,'background'],['button_card_templates','opaque'],['views',0,'cards',0,'name'],['views',0,'cards',1,'cards',0,'card_mod'],['views',-1,'title'],['views',True,'title'],['views','0','title'],['views']]:
            with self.subTest(path=path):
                status,_=self.request('POST',base+'/native-edit',{'revision':2,'edits':[{'path':['title'],'value':'Must roll back'},{'path':path,'value':'tamper'}]})
                self.assertEqual(status,422)
                self.assertEqual(self.f.store.get('alice',d['id']),before)
        for patch in [{'native':{}},{'nativeImport':{}},{'views':[]}]:
            self.assertEqual(self.request('POST',base+'/save',{'revision':2,'patch':patch})[0],400)

if __name__=='__main__':unittest.main()
