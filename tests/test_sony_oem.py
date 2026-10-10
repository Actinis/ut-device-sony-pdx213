import hashlib
from pathlib import Path
import sys
import struct
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from verify_sony_oem import extract, logical_identity, prepare_fastboot


class SonyOEM(unittest.TestCase):
    def fixture(self, root):
        archive = root/'oem.zip'
        with zipfile.ZipFile(archive, 'w') as stream:
            stream.writestr('official.img', b'fixture-image')
            stream.writestr('../outside', b'not-extracted')
        return archive, {'archive': {'sha256': hashlib.sha256(archive.read_bytes()).hexdigest()},
                         'filename': 'official.img', 'bytes': 13,
                         'sha256': hashlib.sha256(b'fixture-image').hexdigest()}

    def test_only_locked_image_is_extracted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); archive, entry = self.fixture(root); output = root/'image'
            extract(archive, output, entry)
            self.assertEqual(output.read_bytes(), b'fixture-image')
            self.assertEqual(sorted(p.name for p in root.iterdir()), ['image', 'oem.zip'])
            with self.assertRaises(ValueError): extract(archive, output, entry)

    def test_changed_archive_or_image_is_rejected(self):
        for field in ('archive', 'image', 'size', 'member'):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                root=Path(directory); archive, entry=self.fixture(root)
                if field == 'archive': entry['archive']['sha256']='a'*64
                if field == 'image': entry['sha256']='a'*64
                if field == 'size': entry['bytes']=14
                if field == 'member': entry['filename']='missing.img'
                with self.assertRaises(ValueError): extract(archive, root/'image', entry)


class FastbootOEM(unittest.TestCase):
    def fixture(self, root):
        path = root/'official.img'
        data = (struct.pack('<I4H4I', 0xed26ff3a, 1, 0, 28, 12, 4096, 4, 3, 0)
                + struct.pack('<HHII', 0xcac1, 0, 1, 4108) + b'A'*4096
                + struct.pack('<HHII', 0xcac2, 0, 2, 16) + b'ABCD'
                + struct.pack('<HHII', 0xcac3, 0, 1, 12))
        path.write_bytes(data)
        decoded = b'A'*4096 + b'ABCD'*2048 + bytes(4096)
        entry = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
                 'decoded_sha256': hashlib.sha256(decoded).hexdigest(), 'decoded_bytes': len(decoded)}
        return path, entry

    def test_conversion_keeps_decoded_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source, entry = self.fixture(root)
            report = prepare_fastboot(source, root/'fastboot.img', entry)
            self.assertEqual(report['decoded'], logical_identity(source))
            self.assertEqual(logical_identity(root/'fastboot.img'), logical_identity(source))
            self.assertNotEqual(report['sha256'], entry['sha256'])

    def test_identity_and_overwrite_rejected(self):
        for field in ('sha256', 'bytes', 'decoded_sha256', 'decoded_bytes', 'existing', 'same'):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); source, entry = self.fixture(root); output = root/'out'
                if field in ('sha256', 'decoded_sha256'): entry[field] = '0'*64
                if field in ('bytes', 'decoded_bytes'): entry[field] += 1
                if field == 'existing': output.write_bytes(b'preserve')
                if field == 'same': output = source
                with self.assertRaises(ValueError): prepare_fastboot(source, output, entry)
                if field == 'existing': self.assertEqual(output.read_bytes(), b'preserve')

    def test_malformed_sparse_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source, entry = self.fixture(root)
            blob = source.read_bytes()
            for content in (blob[:12], blob[:-1], blob + b'extra', blob[:28] + bytes(12) + blob[40:]):
                source.write_bytes(content)
                with self.assertRaises(ValueError): logical_identity(source)
