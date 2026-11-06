import unittest,sys,pathlib,tempfile,copy
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'lumo_raumstudio'))
from store import Store
from peer import CONFIG
class ImportTests(unittest.TestCase):
    def test_native_copy_and_duplicate_are_independent(self):
        with tempfile.TemporaryDirectory() as t:
            s=Store(pathlib.Path(t)/'s.sqlite');cfg=copy.deepcopy(CONFIG);d=s.import_native('alice','Kopie',cfg)
            self.assertIsInstance(d,dict,'Import must commit its independent local management envelope')
            self.assertEqual(d['native'],cfg);self.assertEqual(len(d['views']),1)
            cfg['views'][0]['title']='Fremdänderung';self.assertEqual(s.get('alice',d['id'])['native'],CONFIG)
            clone=s.duplicate('alice',d['id'],1)
            self.assertNotEqual(d['id'],clone['id']);self.assertEqual(clone['native'],CONFIG)
if __name__=='__main__':unittest.main()
