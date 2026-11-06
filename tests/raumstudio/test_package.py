import unittest,pathlib,json,hashlib,ast
ROOT=pathlib.Path(__file__).resolve().parents[2];APP=ROOT/'lumo_raumstudio'
class PackageTests(unittest.TestCase):
    def test_package_has_fixed_start_assets_dependency_and_no_ha_writer(self):
        cfg=json.loads((APP/'config.json').read_text());self.assertEqual((cfg['name'],cfg['slug'],cfg['version']),('LUMO Raumstudio','lumo_raumstudio','0.12.0'));self.assertEqual(cfg['backup'],'cold');self.assertNotIn('ports',cfg);self.assertFalse(cfg['host_network']);self.assertEqual(cfg['options'],{'enabled':False,'allowed_user_ids':[]})
        docker=(APP/'Dockerfile').read_text();self.assertIn('7984cf56ceaddebe4fefeb75d64000b9f45d8b77b11a09b24524da6cdc3af0c8',docker);self.assertIn('--require-hashes',docker);self.assertIn('--only-binary=:all:',docker);self.assertIn('bootstrap.py',docker)
        for line in docker.splitlines():
            if line.startswith('COPY '):
                for name in line.split()[1:-1]:self.assertTrue((APP/name).is_file(),name)
        for f in ('README.md','DOCS.md','CHANGELOG.md','logo.png'):self.assertTrue((APP/f).is_file())
        self.assertEqual(hashlib.sha256((APP/'lumo-logo.png').read_bytes()).hexdigest(),'702cb856a72674a7f2f9214d6a9da788b87b3651208e0abeba4e8afac07fecd0')
        tree=ast.parse((APP/'client.py').read_text());client=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='CoreClient');self.assertEqual({n.name for n in client.body if isinstance(n,ast.FunctionDef)},{'__init__','__repr__','_websocket','_ws_reads'})
        for source in APP.glob('*.py'):
            self.assertNotIn('lovelace/config/save',source.read_text());self.assertNotIn('lovelace/dashboards/create',source.read_text());self.assertNotIn('services/light',source.read_text())
        self.assertNotIn('localStorage',(APP/'app.js').read_text());self.assertNotIn('innerHTML',(APP/'app.js').read_text())
if __name__=='__main__':unittest.main()
