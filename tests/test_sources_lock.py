import importlib.util
import json
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('sources_lock',Path(__file__).resolve().parents[1]/'tools/sources_lock.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class Lock(unittest.TestCase):
    def test_repository_and_missing_dependencies(self):
        root=Path(__file__).resolve().parents[1]
        data=json.loads((root/'sources.lock.json').read_text())
        module.validate(data,root)
        for name in list(data['sources']):
            bad=json.loads(json.dumps(data));del bad['sources'][name]
            with self.assertRaises(ValueError):module.validate(bad)
    def test_vendor_report_is_a_pinned_distinct_external_input(self):
        data=json.loads((Path(__file__).resolve().parents[1]/'sources.lock.json').read_text())
        for key,value in [('url','http://example.org/report'),('sha256','unpinned'),('filename','../report'),('filename',data['sources']['vendor']['filename']),('bytes',0),('bytes',True),('kind','manual')]:
            bad=json.loads(json.dumps(data));bad['sources']['vendor']['build_report'][key]=value
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):module.validate(bad)

    def test_wrong_release_and_unpinned_git(self):
        data=json.loads((Path(__file__).resolve().parents[1]/'sources.lock.json').read_text())
        data['ubuntu_touch']='20.04'
        with self.assertRaises(ValueError):module.validate(data)
        data['ubuntu_touch']='24.04';data['sources']['kernel']['commit']='0'*40
        with self.assertRaises(ValueError):module.validate(data)

    def test_gnss_origin_dependencies_and_source_inventory(self):
        root=Path(__file__).resolve().parents[1]
        data=json.loads((root/'sources.lock.json').read_text())
        for change in ('origin','dependency','source'):
            bad=json.loads(json.dumps(data));gnss=bad['sources']['gnss']
            if change=='origin':gnss['origins']['platform_api']['commit']='0'
            if change=='dependency':gnss['dependencies'].remove('halium_gsi')
            if change=='source':del gnss['files']['device/gnss/gnss.cpp']
            with self.assertRaises(ValueError):module.validate(bad,root)

    def test_nfc_inventory_and_dependency_mutations(self):
        root=Path(__file__).resolve().parents[1]
        data=json.loads((root/'sources.lock.json').read_text())
        for change in ('dependency','missing','stale','hash'):
            bad=json.loads(json.dumps(data));nfc=bad['sources']['nfc']
            if change=='dependency':nfc['dependencies'].remove('gnss')
            if change=='missing':del nfc['files']['device/nfc/inputs.json']
            if change=='stale':nfc['files']['device/nfc/nonexistent']='a'*64
            if change=='hash':nfc['files']['device/nfc/inputs.json']='b'*64
            with self.subTest(change=change),self.assertRaises(ValueError):module.validate(bad,root)

    def test_nfc_package_patch_and_revision_mutations(self):
        root=Path(__file__).resolve().parents[1]/'device/nfc'
        data=json.loads((root/'inputs.json').read_text())
        for change in ('revision','patch','hash','package','url','filename'):
            bad=json.loads(json.dumps(data))
            if change=='revision':bad['sources'][0]['commit']='main'
            if change=='patch':bad['sources'][0]['patch']='../outside.patch'
            if change=='hash':bad['sources'][0]['patch_sha256']='a'*64
            if change=='package':bad['development_headers'].pop()
            if change=='url':bad['development_headers'][0]['url']='http://example.org/package.deb'
            if change=='filename':bad['development_headers'][0]['filename']='../escape.deb'
            with self.subTest(change=change),self.assertRaises(ValueError):module.validate_nfc_inputs(bad,root)
