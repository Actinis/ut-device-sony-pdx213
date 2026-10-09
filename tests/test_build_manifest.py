import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))
import build_manifest as manifest
import package_userdata as package


class CompletedBuild(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.data = Path(self.temp.name)
        self.build = self.data / 'builds/pdx213/test-build'
        self.identity = {
            'schema_version': 2, 'build_id': 'test-build',
            'device_commit': 'a' * 40, 'lock_sha256': 'b' * 64,
            'sources': {'kernel': {'commit': 'c' * 40}, 'rootfs': {'sha256': 'd' * 64}},
        }
        manifest.prepare_build(self.build, self.identity)
        out = self.build / 'out'
        for name in manifest.REQUIRED_ARTIFACTS:
            (out / name).write_bytes(name.encode())
        (out / 'utxperia-reboot-bootloader').chmod(0o755)
        self.release = '4.19.248-test'
        self.modules = out / 'modules/lib/modules' / self.release
        self.modules.mkdir(parents=True)
        for name in ['modules.dep', 'modules.order', 'modules.builtin', 'lcd.ko']:
            (self.modules / name).write_bytes(name.encode())
        manifest.write_report(self.build, self.identity, self.release)

    def report(self, mutate):
        path = self.build / 'out/build-report.json'
        value = json.loads(path.read_text())
        mutate(value)
        path.write_text(json.dumps(value))

    def test_complete_report_and_content_survive_report_write(self):
        modules = manifest.verify_build(self.build, self.identity)
        self.assertEqual(modules, self.build / 'out/modules/lib/modules')
        report = json.loads((self.build / 'out/build-report.json').read_text())
        self.assertNotIn('build-report.json', report['artifacts'])
        manifest.write_report(self.build, self.identity, self.release)
        manifest.verify_build(self.build, self.identity)

    def test_reject_other_commit_lock_dependencies_and_build_id(self):
        for key, value in [('device_commit', 'f' * 40), ('lock_sha256', 'e' * 64),
                           ('build_id', 'other'), ('sources', {'kernel': {'commit': 'f' * 40}})]:
            with self.subTest(key=key):
                expected = copy.deepcopy(self.identity)
                expected[key] = value
                with self.assertRaises(ValueError):
                    manifest.verify_build(self.build, expected)

    def test_report_must_match_the_input_marker(self):
        self.report(lambda r: r['sources']['kernel'].update(commit='e' * 40))
        with self.assertRaises(ValueError):
            manifest.verify_build(self.build, self.identity)

    def test_changed_helper_and_permissions_are_rejected(self):
        helper = self.build / 'out/utxperia-reboot-bootloader'
        helper.write_bytes(b'helper from another build')
        with self.assertRaises(ValueError):
            manifest.verify_build(self.build, self.identity)
        helper.write_bytes(b'utxperia-reboot-bootloader')
        helper.chmod(0o644)
        with self.assertRaises(ValueError):
            manifest.verify_build(self.build, self.identity)

    def test_missing_helpers_modules_and_extra_module_fail(self):
        for name in ['dtbo.img', 'libvndservicemanager-apparmor-compat.so',
                     'modules/lib/modules/' + self.release + '/lcd.ko',
                     'modules/lib/modules/' + self.release + '/modules.dep']:
            path = self.build / 'out' / name
            original = path.read_bytes()
            path.unlink()
            with self.subTest(name=name), self.assertRaises(ValueError):
                manifest.verify_build(self.build, self.identity)
            path.write_bytes(original)
        (self.modules / 'unexpected.ko').write_bytes(b'another build')
        with self.assertRaises(ValueError):
            manifest.verify_build(self.build, self.identity)

    def test_missing_required_records_and_mixed_releases_fail(self):
        self.report(lambda r: r['artifacts'].pop('dtbo.img'))
        with self.assertRaises(ValueError):
            manifest.verify_build(self.build, self.identity)
        manifest.write_report(self.build, self.identity, self.release)
        extra = self.build / 'out/modules/lib/modules/other-release'
        extra.mkdir()
        (extra / 'stale.ko').write_bytes(b'old')
        with self.assertRaises(ValueError):
            manifest.write_report(self.build, self.identity, self.release)

    def test_output_and_artifact_links_fail(self):
        out = self.build / 'out'
        out.rename(self.build / 'original-out')
        out.symlink_to(self.build / 'original-out', target_is_directory=True)
        with self.assertRaises(ValueError):
            manifest.verify_build(self.build, self.identity)
        out.unlink()
        (self.build / 'original-out').rename(out)
        helper = out / 'utxperia-reboot-bootloader'
        helper.rename(self.build / 'foreign-helper')
        helper.symlink_to(self.build / 'foreign-helper')
        with self.assertRaises(ValueError):
            manifest.verify_build(self.build, self.identity)

    def test_legacy_and_missing_report_fail(self):
        path = self.build / 'out/build-report.json'
        path.write_text(json.dumps({'sources': self.identity['sources'], 'artifacts': {}}))
        with self.assertRaises(ValueError):
            manifest.verify_build(self.build, self.identity)
        path.unlink()
        with self.assertRaises(FileNotFoundError):
            manifest.verify_build(self.build, self.identity)

    def test_resume_rejects_stale_inputs_without_mutating_output(self):
        report = self.build / 'out/build-report.json'
        before = report.read_bytes()
        stale = dict(self.identity, device_commit='f' * 40)
        with self.assertRaises(ValueError):
            manifest.prepare_build(self.build, stale, resume=True)
        self.assertEqual(report.read_bytes(), before)
        (self.build / 'input-identity.json').unlink()
        with self.assertRaises(ValueError):
            manifest.prepare_build(self.build, self.identity, resume=True)
        self.assertEqual(report.read_bytes(), before)

    def test_valid_resume_invalidates_completed_report(self):
        manifest.prepare_build(self.build, self.identity, resume=True)
        self.assertFalse((self.build / 'out/build-report.json').exists())

    def test_package_preflight_fails_before_output_or_vendor_access(self):
        (self.modules / 'lcd.ko').unlink()
        args = ['package_userdata.py', '--build-id', 'test-build', '--vendor', '/missing/vendor']
        for tool in ['mksquashfs', 'mke2fs', 'img2simg', 'avbtool']:
            args += ['--' + tool, '/missing/tool']
        with patch.dict(os.environ, UT_PORTS_DATA_DIR=str(self.data), FAKEROOTKEY='test'), \
                patch.object(sys, 'argv', args), \
                patch.object(package, 'build_identity', return_value=self.identity), \
                self.assertRaises(SystemExit) as result:
            package.main()
        self.assertEqual(result.exception.code, 2)
        self.assertFalse((self.build / 'userdata-package').exists())


if __name__ == '__main__':
    unittest.main()
