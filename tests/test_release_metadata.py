import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('release_metadata', Path(__file__).resolve().parents[1] / 'tools/release_metadata.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class Packaging(unittest.TestCase):
    def test_metadata_and_invalid_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            images = root/'images'; images.mkdir()
            tag = 'pdx213-noble-port-v0.1.0'
            image = images/(tag+'-boot.img'); image.write_bytes(b'fixture image')
            lock = root/'lock.json'
            data = {'status':'locked', 'schema_version':1, 'device':'sony-pdx213', 'ubuntu_touch':'24.04', 'sources':{'kernel':{'url':'https://example.org/kernel','commit':'a'*40}, **{name:{'url':'https://example.org/'+name,'version':'fixture','sha256':'b'*64} for name in ['rootfs','halium_gsi','toolchain']}}}
            lock.write_text(json.dumps(data))
            args = [images, root/'metadata', lock, 'c'*40, tag, 'https://github.com/Actinis/ut-device-sony-pdx213/actions/runs/123']
            module.package(*args)
            manifest = json.loads((args[1]/'release-manifest.json').read_text())
            self.assertEqual(manifest['artifacts'][0]['sha256'], hashlib.sha256(image.read_bytes()).hexdigest())
            self.assertEqual(manifest['qualification'], 'pending')
            self.assertIn('release-manifest.json', (args[1]/'SHA256SUMS').read_text())
            with self.assertRaises(ValueError): module.package(*args)
            args[1] = root/'other'
            data['status'] = 'unpopulated'; lock.write_text(json.dumps(data))
            with self.assertRaises(ValueError): module.package(*args)
            self.assertFalse(args[1].exists())
            data['status'] = 'locked'; lock.write_text(json.dumps(data))
            stray = images/'private-backup.img'; stray.write_bytes(b'backup')
            with self.assertRaises(ValueError): module.package(*args)
            stray.unlink(); image.unlink(); image.symlink_to(lock)
            with self.assertRaises(ValueError): module.package(*args)
            image.unlink(); image.write_bytes(b'')
            with self.assertRaises(ValueError): module.package(*args)
