"""B1: upgrade real pinned 0.12.0 Store bytes, never a forged legacy envelope."""
from contextlib import closing
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'lumo_raumstudio'))
from store import Store, StudioError
import maintenance

BASELINE = 'c1ffa3434d95a59f0538573173d8138927388811'
CONFIG = {'views': [
    {'title': title, 'cards': [
        {'type': 'entity', 'entity': 'sensor.x', 'name': 'ä' * 200}
        for _ in range(512)]}
    for title in ('A', 'B')]}


def document_bytes(path):
    with closing(sqlite3.connect(path)) as connection:
        return connection.execute('SELECT document FROM dashboards').fetchone()[0].encode('utf-8')


class LegacyUnicodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline_tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.baseline_tmp.cleanup)
        root = Path(cls.baseline_tmp.name)
        baseline = root / 'baseline'
        baseline.mkdir()
        archive = subprocess.check_output(['git', 'archive', '--format=tar', BASELINE], cwd=ROOT)
        # Only repository-owned paths from the pinned local commit, no downloads.
        with tarfile.open(fileobj=io.BytesIO(archive)) as source:
            source.extractall(baseline, filter='data')
        cls.database = root / 'baseline.sqlite'
        fixture = root / 'config.json'
        fixture.write_text(json.dumps(CONFIG), encoding='utf-8')
        generated = subprocess.run([
            sys.executable, '-I', '-B', '-c',
            'import json,sys; from pathlib import Path; '
            'sys.path.insert(0,sys.argv[1]); from store import Store; '
            'from maintenance import inspect; '
            's=Store(sys.argv[2]); '
            'd=s.import_native("alice","Legacy Unicode",json.loads(Path(sys.argv[3]).read_text())); '
            'assert "nativeImport" not in d; '
            'assert Store(s.path).get("alice",d["id"])==d; '
            'assert inspect(s.path)==2; '
            'print(json.dumps({"schema":2,"legacy":True,"baselineAccepted":True}))',
            str(baseline / 'lumo_raumstudio'), str(cls.database), str(fixture)
        ], check=True, capture_output=True, text=True, cwd=baseline)
        cls.raw = document_bytes(cls.database)
        cls.document = json.loads(cls.raw)
        cls.database_hash = hashlib.sha256(cls.database.read_bytes()).hexdigest()
        # Optional synthetic evidence only; never household data or configs.
        if os.environ.get('RAUMSTUDIO_LEGACY_EVIDENCE'):
            out = Path(os.environ['RAUMSTUDIO_LEGACY_EVIDENCE'])
            out.mkdir(parents=True, exist_ok=False)
            shutil.copyfile(cls.database, out / 'baseline.sqlite')
            (out / 'baseline-generation.json').write_text(json.dumps({
                'commit': BASELINE,
                'archiveSha256': hashlib.sha256(archive).hexdigest(),
                'databaseSha256': cls.database_hash,
                'documentSha256': hashlib.sha256(cls.raw).hexdigest(),
                'utf8Bytes': len(json.dumps(CONFIG, ensure_ascii=False).encode('utf-8')),
                'asciiBytes': len(json.dumps(CONFIG, ensure_ascii=True).encode('utf-8')),
                'baselineStdout': generated.stdout,
                'baselineStderr': generated.stderr,
                'baselineExitCode': generated.returncode,
            }, indent=2) + '\n', encoding='utf-8')

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / 'legacy.sqlite'
        shutil.copyfile(self.database, self.path)
        self.assertLess(len(json.dumps(CONFIG, ensure_ascii=False).encode('utf-8')), 1048576)
        self.assertGreater(len(json.dumps(CONFIG, ensure_ascii=True).encode('utf-8')), 1048576)
        self.assertNotIn('nativeImport', self.document)
        self.assertEqual(document_bytes(self.path), self.raw)

    def assert_legacy_unchanged(self, path):
        self.assertEqual(document_bytes(path), self.raw, 'Legacy document bytes must not be rewritten')
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), self.database_hash)
        self.assertEqual(Store(path).get('alice', self.document['id']), self.document)
        self.assertEqual(document_bytes(path), self.raw)

    def test_pinned_legacy_unicode_store_startup_preserves_document(self):
        try:
            reopened = Store(self.path)
        except StudioError as error:
            self.fail('Pinned 0.12.0 Unicode database must open: ' + str(error))
        self.assertEqual(reopened.get('alice', self.document['id']), self.document)
        self.assert_legacy_unchanged(self.path)

    def test_pinned_legacy_unicode_backup_preserves_document(self):
        snapshot = self.root / 'backup.sqlite'
        try:
            maintenance.backup(self.path, snapshot)
        except StudioError as error:
            self.fail('Pinned 0.12.0 Unicode database must back up: ' + str(error))
        self.assertEqual(maintenance.inspect(snapshot), 2)
        self.assertEqual(document_bytes(snapshot), self.raw)
        self.assertEqual(Store(snapshot).get('alice', self.document['id']), self.document)
        restored = self.root / 'roundtrip.sqlite'
        Store(restored)
        maintenance.restore(snapshot, restored)
        self.assertEqual(document_bytes(restored), self.raw)
        self.assertEqual(Store(restored).get('alice', self.document['id']), self.document)
        self.assert_legacy_unchanged(self.path)

    def test_pinned_legacy_unicode_restore_preserves_document(self):
        target = self.root / 'restored.sqlite'
        Store(target).create('alice', 'Replace this local synthetic draft')
        try:
            maintenance.restore(self.path, target)
        except StudioError as error:
            self.fail('Pinned 0.12.0 Unicode database must restore: ' + str(error))
        self.assertEqual(maintenance.inspect(target), 2)
        self.assertEqual(document_bytes(target), self.raw)
        self.assertEqual(Store(target).get('alice', self.document['id']), self.document)
        self.assert_legacy_unchanged(self.path)

    def test_new_native_import_keeps_ascii_limit_and_legacy_keeps_utf8_limit(self):
        from dashboard_reads import bounded, validate_configuration, validate_supported_configuration
        store = Store(self.root / 'new.sqlite')
        for validate in (bounded, validate_configuration,
                         lambda config: store.import_native('alice', 'New Unicode', config)):
            with self.subTest(bound=validate.__name__):
                with self.assertRaisesRegex(StudioError, '1 MiB'):
                    validate(CONFIG)
        self.assertEqual(store.list('alice'), [])
        too_large = {'views': [dict(view, title=str(i))
                              for i, view in enumerate(CONFIG['views'] * 3)]}
        self.assertGreater(len(json.dumps(too_large, ensure_ascii=False).encode('utf-8')), 1048576)
        with self.assertRaisesRegex(StudioError, '1 MiB'):
            validate_supported_configuration(too_large)
        # Existing new-format documents must not acquire the legacy size exemption.
        imported = store.import_native('alice', 'New small', {'views': []})
        imported['native'] = CONFIG
        with store.connect() as connection:
            connection.execute('UPDATE dashboards SET document=? WHERE id=?',
                               (json.dumps(imported), imported['id']))
        with self.assertRaisesRegex(StudioError, '1 MiB'):
            maintenance.inspect(store.path)
        self.assert_legacy_unchanged_source()

    def assert_legacy_unchanged_source(self):
        self.assertEqual(document_bytes(self.database), self.raw)
        self.assertEqual(hashlib.sha256(self.database.read_bytes()).hexdigest(), self.database_hash)


if __name__ == '__main__':
    unittest.main()
