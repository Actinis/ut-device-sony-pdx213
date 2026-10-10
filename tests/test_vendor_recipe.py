import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from build_vendor import projects
from prepare_ci_userdata import check_vendor, fetch
from sources_lock import validate


class VendorRecipe(unittest.TestCase):
    def test_manifest_is_pinned_and_rejects_unsafe_inputs(self):
        path = ROOT/'device/vendor/manifest.xml'
        expected = projects(path)
        self.assertEqual(len(expected), 733)
        for mode in ('path', 'commit', 'duplicate', 'patches'):
            tree = ET.parse(path)
            root = tree.getroot()
            project = root.find('project')
            if mode == 'path': project.set('path', '../outside')
            if mode == 'commit': project.set('revision', 'main')
            if mode == 'duplicate': root.append(copy.deepcopy(project))
            if mode == 'patches':
                for node in root.findall('project'):
                    if node.get('path') == 'rpm': root.remove(node)
            with tempfile.TemporaryDirectory() as directory:
                candidate = Path(directory)/'manifest.xml'; tree.write(candidate)
                with self.subTest(mode=mode), self.assertRaises(ValueError): projects(candidate)

    def test_current_manual_vendor_cannot_be_uploaded_as_full_image(self):
        lock = json.loads((ROOT/'sources.lock.json').read_text())
        validate(lock, ROOT)
        with self.assertRaises(ValueError): check_vendor(lock['sources']['vendor'])
        entry = dict(lock['sources']['vendor'], kind='artifact')
        with self.assertRaises(ValueError): check_vendor(entry)
        entry['redistribution_approved'] = True
        self.assertIs(check_vendor(entry), entry)

    def test_corrupt_cached_input_is_rejected_before_packaging(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory); (path/'vendor.img').write_bytes(b'wrong')
            with self.assertRaises(ValueError):
                fetch({'filename': 'vendor.img', 'sha256': 'a'*64}, path)

    def test_recipe_inventory_and_avb_decoded_hash_are_required(self):
        original = json.loads((ROOT/'sources.lock.json').read_text())
        for mode in ('recipe', 'decoded'):
            bad = copy.deepcopy(original)
            if mode == 'recipe': bad['sources']['vendor_recipe']['files'].pop('tools/build_vendor.py')
            else: bad['sources']['avbtool']['decoded_sha256'] = 'not-a-hash'
            with self.subTest(mode=mode), self.assertRaises(ValueError): validate(bad, ROOT)
