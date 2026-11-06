from contextlib import closing
import unittest,tempfile,pathlib,sys,sqlite3
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'lumo_raumstudio'))
import maintenance
from store import Store
from test_images import png
class MaintenanceTests(unittest.TestCase):
    def test_verified_backup_restore_migration_rollback(self):
        with tempfile.TemporaryDirectory() as t:
            p=pathlib.Path(t);s=Store(p/'live.sqlite');d=s.create('alice','Gesichert');image=s.put_image('alice','Foto',png())
            maintenance.backup(s.path,p/'backup.sqlite')
            self.assertTrue((p/'backup.sqlite').is_file(),'Backup must contain the real SQLite snapshot')
            s.update('alice',d['id'],1,{'name':'Änderung'})
            maintenance.restore(p/'backup.sqlite',s.path)
            self.assertEqual(Store(s.path).get('alice',d['id']),d);self.assertEqual(s.image('alice',image['id'])[1],png())
            # Exercise the real supported schema-1 -> schema-2 migration.
            with closing(sqlite3.connect(s.path)) as c, c:
                c.execute('DROP INDEX IF EXISTS dashboards_owner');c.execute('PRAGMA user_version=1')
            before=s.path.read_bytes();Store(s.path)
            backs=list(p.glob('live.sqlite.pre-v1-*.sqlite'));self.assertEqual(len(backs),1)
            self.assertEqual(Store(s.path).get('alice',d['id']),d)
            with closing(sqlite3.connect(s.path)) as c, c:self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0],2)
            maintenance.restore(backs[0],s.path,expected_version=1)
            with closing(sqlite3.connect(s.path)) as c, c:self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0],1)
            with self.assertRaises(Exception):maintenance.migrate(s.path,inject_failure=True)
            with closing(sqlite3.connect(s.path)) as c, c:self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0],1)
            self.assertEqual(s.get('alice',d['id']),d)
            (p/'broken').write_bytes(b'not a database');before=s.path.read_bytes()
            with self.assertRaises(Exception):maintenance.restore(p/'broken',s.path)
            self.assertEqual(s.path.read_bytes(),before)
    def test_corrupt_backup_content_cannot_replace_good_database(self):
        with tempfile.TemporaryDirectory() as t:
            p=pathlib.Path(t);s=Store(p/'live.sqlite');d=s.create('alice','Unverändert');maintenance.backup(s.path,p/'backup.sqlite')
            import json
            with closing(sqlite3.connect(p/'backup.sqlite')) as c, c:
                bad=dict(d);bad['name']='';c.execute('UPDATE dashboards SET document=?',(json.dumps(bad),))
            before=s.path.read_bytes()
            with self.assertRaises(Exception):maintenance.restore(p/'backup.sqlite',s.path)
            self.assertEqual(s.path.read_bytes(),before)
if __name__=='__main__':unittest.main()
