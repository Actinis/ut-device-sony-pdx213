import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from verify_sony_oem import extract


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
