import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from sources_lock import validate, validate_camera_inputs


class CameraInputs(unittest.TestCase):
    def test_complete_locked_source_and_generator(self):
        lock = json.loads((ROOT / 'sources.lock.json').read_text())
        validate(lock, ROOT)
        inputs = json.loads((ROOT / 'device/camera/inputs.json').read_text())
        self.assertEqual(len(validate_camera_inputs(inputs, ROOT / 'device/camera')['development_packages']), 22)

    def test_incomplete_or_unsafe_inputs_rejected(self):
        original = json.loads((ROOT / 'device/camera/inputs.json').read_text())
        for mode in ('source', 'patch', 'generator', 'missing', 'duplicate', 'filename', 'hash'):
            inputs = copy.deepcopy(original)
            if mode == 'source': inputs['source']['commit'] = '0' * 40
            elif mode == 'patch': inputs['source']['patch'] = '../elsewhere.patch'
            elif mode == 'generator': inputs['moc']['path'] = '../moc'
            elif mode == 'missing': inputs['development_packages'].pop()
            elif mode == 'duplicate': inputs['development_packages'][-1] = inputs['development_packages'][0]
            elif mode == 'filename': inputs['development_packages'][0]['filename'] = '../sdk.deb'
            elif mode == 'hash': inputs['source']['patch_sha256'] = '0' * 64
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                validate_camera_inputs(inputs, ROOT / 'device/camera')

    def test_camera_cannot_disappear_from_lock(self):
        lock = json.loads((ROOT / 'sources.lock.json').read_text())
        lock['sources'].pop('camera')
        with self.assertRaises(ValueError): validate(lock, ROOT)
