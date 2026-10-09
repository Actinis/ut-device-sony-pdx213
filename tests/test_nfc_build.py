import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import build_nfc as nfc

class Resume(unittest.TestCase):
    def test_resume_requires_same_inputs_and_complete_regular_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);out=root/'out';out.mkdir();work=root/'work'
            identity={'fixture':'locked runtime'}
            for name in nfc.ARTIFACTS:(out/name).write_bytes(name.encode())
            report={'runtime_identity':identity,
                    'inputs_sha256':nfc.digest(nfc.ROOT/'device/nfc/inputs.json'),
                    'lock_sha256':nfc.digest(nfc.ROOT/'sources.lock.json'),
                    'artifacts':{name:nfc.digest(out/name) for name in nfc.ARTIFACTS}}
            path=out/'nfc-build-report.json'
            def attempt():nfc.build(root,root,root,root,work,out,root/'downloads')
            with patch.object(nfc,'runtime_identity',return_value=identity):
                path.write_text(json.dumps(report));attempt()
                for key in ('runtime_identity','inputs_sha256','lock_sha256','artifacts'):
                    bad=copy.deepcopy(report);bad[key]={} if isinstance(bad[key],dict) else 'changed'
                    path.write_text(json.dumps(bad))
                    with self.subTest(key=key),self.assertRaises(ValueError):attempt()
                path.write_text(json.dumps(report))
                artifact=out/nfc.ARTIFACTS[0];artifact.unlink()
                with self.assertRaises(ValueError):attempt()
                other=root/'foreign';other.write_bytes(nfc.ARTIFACTS[0].encode());artifact.symlink_to(other)
                with self.assertRaises(ValueError):attempt()
                self.assertFalse(work.exists())
