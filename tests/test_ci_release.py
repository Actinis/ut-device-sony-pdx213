import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import build_manifest
import publish_ci_release as release


class Publication(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.lock_bytes = (Path(__file__).resolve().parents[1] / 'sources.lock.json').read_bytes()
        self.lock = json.loads(self.lock_bytes)
        self.run = {'id': 123, 'run_attempt': 1, 'status': 'completed', 'conclusion': 'success',
                    'event': 'push', 'path': '.github/workflows/build.yml', 'head_branch': 'main',
                    'head_sha': 'a' * 40, 'html_url': 'https://github.com/Actinis/ut-device-sony-pdx213/actions/runs/123',
                    'repository': {'full_name': release.REPOSITORY}, 'head_repository': {'full_name': release.REPOSITORY}}
        self.download = self.root / 'download'; self.download.mkdir()
        self.build = self.root / 'build'
        identity = {'schema_version': 2, 'build_id': 'ci-123-1', 'device_commit': 'a'*40,
                    'lock_sha256': hashlib.sha256(self.lock_bytes).hexdigest(), 'sources': self.lock['sources']}
        build_manifest.prepare_build(self.build, identity)
        for name in build_manifest.REQUIRED_ARTIFACTS:
            (self.build/'out'/name).write_bytes(name.encode())
        (self.build/'out/utxperia-reboot-bootloader').chmod(0o755)
        modules = self.build/'out/modules/lib/modules/test-release'; modules.mkdir(parents=True)
        for name in ['modules.dep', 'modules.order', 'modules.builtin', 'driver.ko']:
            (modules/name).write_bytes(name.encode())
        build_manifest.write_report(self.build, identity, 'test-release')
        self.archive()

    def archive(self):
        with tarfile.open(self.download/'pdx213-noble-kernel-boot.tar.gz', 'w:gz') as stream:
            stream.add(self.build/'out', arcname='out')
            stream.add(self.build/'input-identity.json', arcname='input-identity.json')
        (self.download/'out').mkdir(exist_ok=True)
        shutil.copyfile(self.build/'out/build-report.json', self.download/'out/build-report.json')
        shutil.copyfile(self.build/'input-identity.json', self.download/'input-identity.json')

    def test_daily_metadata_and_all_asset_hashes(self):
        output = self.root/'release'
        tag, title, notes, draft = release.prepare(self.download, output, self.lock_bytes, self.run)
        self.assertIn('ut24.04-2.x-daily-123-1-aaaaaaa', tag)
        self.assertFalse(draft)
        manifest = json.loads((output/'release-manifest.json').read_text())
        self.assertEqual(manifest['channel'], 'daily')
        self.assertIsNone(manifest['port_version'])
        self.assertEqual(manifest['qualification'], 'pending')
        self.assertIn('Not a complete installable', notes)
        for line in (output/'SHA256SUMS').read_text().splitlines():
            checksum, name = line.split('  ')
            self.assertEqual(checksum, build_manifest.sha(output/name))
        self.assertEqual(len(list(output.iterdir())), 8)

    def test_version_tag_is_a_candidate_draft(self):
        self.run['head_branch'] = 'pdx213-noble-port-v0.1.0'
        tag, _, _, draft = release.prepare(self.download, self.root/'release', self.lock_bytes, self.run)
        self.assertEqual(tag, self.run['head_branch'])
        self.assertTrue(draft)

    def test_reject_untrusted_unsuccessful_or_non_main_run(self):
        for key, value in [('conclusion', 'failure'), ('event', 'pull_request'),
                           ('head_branch', 'feature'), ('path', '.github/workflows/checks.yml')]:
            bad = copy.deepcopy(self.run); bad[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): release.check_run(bad)
        bad = copy.deepcopy(self.run); bad['head_repository']['full_name'] = 'someone/fork'
        with self.assertRaises(ValueError): release.check_run(bad)

    def test_reject_wrong_source_commit_and_changed_helper(self):
        self.run['head_sha'] = 'b'*40
        with self.assertRaises(ValueError):
            release.prepare(self.download, self.root/'release', self.lock_bytes, self.run)
        shutil.rmtree(self.download/'verified-build')
        self.run['head_sha'] = 'a'*40
        (self.build/'out/utxperia-reboot-bootloader').write_bytes(b'changed')
        self.archive()
        with self.assertRaises(ValueError):
            release.prepare(self.download, self.root/'release', self.lock_bytes, self.run)
        self.assertFalse((self.root/'release').exists())

    def test_archive_escape_and_links_are_rejected(self):
        for name, kind in [('../escape', tarfile.REGTYPE), ('out/linked', tarfile.SYMTYPE)]:
            with tarfile.open(self.download/'bad.tar.gz', 'w:gz') as stream:
                entry = tarfile.TarInfo(name); entry.type = kind; entry.linkname = '/etc/passwd' if kind == tarfile.SYMTYPE else ''
                stream.addfile(entry)
            with self.subTest(name=name), self.assertRaises(ValueError):
                release.extract(self.download/'bad.tar.gz', self.root/'extracted')


if __name__ == '__main__':
    unittest.main()
