import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from prepare_install_bundle import require_file, require_raw_sparse, stage
from build_manifest import sha

class InstallBundleTests(unittest.TestCase):
    def test_equivalent_fill_is_rejected_for_sony(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'oem.img'
            p.write_bytes(struct.pack('<I4H4I',0xed26ff3a,1,0,28,12,4096,1,1,0)
                          +struct.pack('<HHII',0xcac2,0,1,16)+bytes(4))
            with self.assertRaisesRegex(ValueError,'FILL'):require_raw_sparse(p)
            p.write_bytes(struct.pack('<I4H4I',0xed26ff3a,1,0,28,12,4096,1,1,0)
                          +struct.pack('<HHII',0xcac1,0,1,4108)+bytes(4096))
            self.assertEqual(require_raw_sparse(p),p)

    def test_truncated_sparse_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'userdata.img';p.write_bytes(bytes(28))
            with self.assertRaises(ValueError):require_raw_sparse(p)

    def test_linked_or_empty_manual_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'file';p.touch();q=Path(d)/'link';q.symlink_to(p)
            for f in [p,q]:
                with self.assertRaises(ValueError):require_file(f)

    def test_local_bundle_covers_all_inputs_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);source=p/'source';source.write_bytes(b'reviewed image')
            out=p/'bundle';stage({'boot.img':source},{'status':'candidate'},out,True)
            self.assertEqual((out/'boot.img').stat().st_ino,source.stat().st_ino)
            sums=(out/'SHA256SUMS').read_text();self.assertIn(sha(out/'boot.img')+'  boot.img',sums)
            self.assertIn(sha(out/'install-manifest.json')+'  install-manifest.json',sums)
            self.assertEqual(out.stat().st_mode&0o777,0o700)
            self.assertIn('vbmeta_system_a',(out/'FLASHING.md').read_text())
            with self.assertRaises(FileExistsError):stage({'boot.img':source},{},out)

if __name__=='__main__':unittest.main()
