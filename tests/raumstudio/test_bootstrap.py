import unittest,sys,subprocess,tempfile,pathlib,os,json
APP=pathlib.Path(__file__).resolve().parents[2]/'lumo_raumstudio'
class BootstrapTests(unittest.TestCase):
    def test_default_options_start_after_irreversible_privilege_drop(self):
        self.assertEqual(os.getuid(),0,'This isolated bootstrap test requires container root, never host root')
        with tempfile.TemporaryDirectory() as t:
            p=pathlib.Path(t);p.chmod(0o755);options=p/'options.json';options.write_text('{"enabled":false,"allowed_user_ids":[]}');options.chmod(0o644)
            script="import sys,os,json;sys.path.insert(0,sys.argv[1]);from bootstrap import prepare;from store import Store;s,c=prepare(sys.argv[2],sys.argv[3]);db=Store(sys.argv[3]+'/studio.sqlite');print(json.dumps({'uid':os.getresuid(),'gid':os.getresgid(),'groups':os.getgroups(),'policy':s.current() is None,'rows':db.list('alice')}))"
            r=subprocess.run([sys.executable,'-c',script,str(APP),str(options),str(p/'raumstudio')],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,'Default configuration must start safely: '+r.stderr)
            result=json.loads(r.stdout);self.assertEqual(result['uid'],[65532]*3);self.assertEqual(result['groups'],[]);self.assertTrue(result['policy']);self.assertEqual(result['rows'],[])
            # No root files are recursively repaired; symlinks fail before touching target.
            foreign=p/'foreign';foreign.mkdir();(foreign/'keep').write_text('unchanged');link=p/'link';link.symlink_to(foreign)
            r=subprocess.run([sys.executable,'-c',script,str(APP),str(options),str(link)],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0);self.assertEqual((foreign/'keep').read_text(),'unchanged');self.assertEqual(foreign.stat().st_uid,0)
if __name__=='__main__':unittest.main()
