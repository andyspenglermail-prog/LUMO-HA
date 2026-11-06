from contextlib import closing
import sys, unittest, tempfile, pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'lumo_raumstudio'))
from store import Store
class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.path=pathlib.Path(self.tmp.name)/'studio.sqlite'; self.s=Store(self.path)
    def tearDown(self): self.tmp.cleanup()
    def test_create_persistent_empty_owned_dashboard(self):
        d=self.s.create('alice','Mein Zuhause','mdi:home')
        self.assertIsInstance(d,dict,'Creation must return a durable dashboard, not a placeholder')
        self.assertEqual(d['views'],[]); self.assertEqual(d['revision'],1)
        self.assertEqual(Store(self.path).get('alice',d['id']),d)
        self.assertEqual(self.s.list('bob'),[])
        with self.assertRaises(Exception): self.s.get('bob',d['id'])
    def test_validation_and_revision_lifecycle(self):
        for bad in ['', '   ', 'x'*81, 'bad\nname', 3, None]:
            with self.subTest(name=bad), self.assertRaises(Exception): self.s.create('alice',bad)
        d=self.s.create('alice','Original'); identifier=d['id']; created=d['createdAt']
        changed=self.s.update('alice',identifier,1,{'name':'Neu'})
        self.assertEqual((changed['id'],changed['createdAt'],changed['revision']),(identifier,created,2))
        with self.assertRaises(Exception):self.s.update('alice',identifier,1,{'name':'Verloren'})
        clone=self.s.duplicate('alice',identifier,2)
        self.s.update('alice',clone['id'],1,{'description':'Unabhängig'})
        self.assertEqual(self.s.get('alice',identifier)['description'],'')
        with self.assertRaises(Exception):self.s.delete('alice',identifier,2,False)
        self.s.delete('alice',identifier,2,True)
        self.assertEqual(len(self.s.list('alice')),1)
    def test_unknown_schema_is_not_overwritten(self):
        import sqlite3
        with closing(sqlite3.connect(self.path)) as c, c:c.execute('PRAGMA user_version=999')
        original=self.path.read_bytes()
        with self.assertRaises(Exception):Store(self.path)
        self.assertEqual(self.path.read_bytes(),original)
    def test_atomic_revision_race(self):
        from concurrent.futures import ThreadPoolExecutor
        d=self.s.create('alice','Race')
        def save(name):
            try:return self.s.update('alice',d['id'],1,{'name':name})['revision']
            except Exception:return 'conflict'
        with ThreadPoolExecutor(2) as p:results=list(p.map(save,['A','B']))
        self.assertCountEqual(results,[2,'conflict'])
    def test_background_settings_are_validated_and_survive(self):
        from store import defaults
        d=self.s.create('alice','Hintergrund'); settings=defaults()
        settings['background'].update(color='#123456',mode='scale',scale=137,opacity=0,attachment='fixed')
        try:changed=self.s.update('alice',d['id'],1,{'settings':settings})
        except Exception as e:self.fail('Gültige Hintergrund-Einstellungen müssen speicherbar sein: '+str(e))
        self.assertEqual(Store(self.path).get('alice',d['id'])['settings'],settings)
        settings['background']['imageId']='foreign'
        with self.assertRaises(Exception):self.s.update('alice',d['id'],2,{'settings':settings})
    def test_invalid_text_never_commits(self):
        from store import StudioError
        before=self.s.list('alice')
        for name in ['\ud800','bad\x7fname']:
            with self.subTest(name=repr(name)),self.assertRaises(StudioError):self.s.create('alice',name)
        self.assertEqual(self.s.list('alice'),before)
if __name__=='__main__': unittest.main()
