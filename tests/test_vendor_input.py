import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from vendor_input import identify_vendor
from build_manifest import sha
from build_vendor import projects

ROOT=Path(__file__).resolve().parents[1]

class VendorInputTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.image=Path(self.temp.name)/'vendor';self.image.write_bytes(b'candidate')
        self.report=Path(self.temp.name)/'report'
        self.sources=json.loads((ROOT/'sources.lock.json').read_text())['sources']
        files=self.sources['vendor_recipe']['files']
        self.record={'vendor_sha256':sha(self.image),
            'recipe':{'manifest_sha256':files['device/vendor/manifest.xml']},
            'container_recipe_sha256':files['device/vendor/Dockerfile'],
            'builder_sha256':files['tools/build_vendor.py'],
            'container_image':'sha256:'+'a'*64,
            'commits':projects(ROOT/'device/vendor/manifest.xml'),
            'patches':{'patches/bionic/'+str(n)+'.patch':'b'*64 for n in range(17)}}
    def check(self,record):
        self.report.write_text(json.dumps(record))
        return identify_vendor(self.image,self.sources,ROOT,self.report,sha(self.report))
    def test_source_report_does_not_approve_distribution(self):
        result=self.check(self.record)
        self.assertEqual(result['kind'],'local-source-candidate')
        self.assertIn('no redistribution approval',result['qualification'])
    def test_missing_or_changed_report_pin_rejected(self):
        self.report.write_text(json.dumps(self.record))
        for pin in (None,'0'*64):
            with self.assertRaises(ValueError):identify_vendor(self.image,self.sources,ROOT,self.report,pin)
    def test_mixed_image_recipe_or_incomplete_inventory_rejected(self):
        for field in ('vendor_sha256','builder_sha256','container_recipe_sha256','commits','patches'):
            bad=copy.deepcopy(self.record);bad[field]={} if field in ('commits','patches') else '0'*64
            with self.assertRaises(ValueError):self.check(bad)
    def test_default_still_requires_locked_vendor(self):
        with self.assertRaises(ValueError):identify_vendor(self.image,self.sources,ROOT)
        sources=copy.deepcopy(self.sources);sources['vendor'].pop('build_report',None);sources['vendor']['sha256']=sha(self.image)
        self.assertEqual(identify_vendor(self.image,sources,ROOT)['kind'],'locked')
    def test_locked_source_requires_exact_provenance_report(self):
        self.report.write_text(json.dumps(self.record))
        self.sources['vendor']['sha256']=sha(self.image)
        self.sources['vendor']['build_report']['sha256']=sha(self.report)
        with self.assertRaisesRegex(ValueError,'requires its pinned build report'):
            identify_vendor(self.image,self.sources,ROOT)
        self.assertEqual(self.check(self.record)['kind'],'locked-source-artifact')
        self.sources['vendor']['build_report']['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'locked vendor provenance'):self.check(self.record)

    def test_vendor_symlink_rejected(self):
        link=Path(self.temp.name)/'link';link.symlink_to(self.image)
        with self.assertRaises(ValueError):identify_vendor(link,self.sources,ROOT)

if __name__=='__main__':unittest.main()
