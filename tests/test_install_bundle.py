import json
from pathlib import Path
import struct
import sys
import tempfile
import tarfile
import hashlib
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from prepare_install_bundle import require_file, require_raw_sparse, stage, flashing_instructions
from prepare_ci_userdata import archive_candidate
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
            self.assertIn(sha(out/'FLASHING.md')+'  FLASHING.md',sums)
            self.assertNotIn('Android 11 firmware/bootloader baseline',(out/'FLASHING.md').read_text())
            self.assertEqual(out.stat().st_mode&0o777,0o700)
            self.assertIn('vbmeta_system_a',(out/'FLASHING.md').read_text())
            with self.assertRaises(FileExistsError):stage({'boot.img':source},{},out)

class FullCandidateInstructions(unittest.TestCase):
    def test_exact_source_and_separate_oem_are_checksum_covered(self):
        with tempfile.TemporaryDirectory() as d:
            build=Path(d);package=build/'userdata-package';package.mkdir()
            out=build/'out';out.mkdir()
            report=out/'build-report.json';report.write_text(json.dumps({'device_commit':'a'*40}))
            image=package/'userdata.img';image.write_bytes(b'userdata fixture')
            # A separately obtained OEM must never be swept into the CI archive.
            (package/'oem.img').write_bytes(b'private owner input')
            archive_candidate(build,package,{'userdata.img':image,'build-report.json':report})
            with tarfile.open(build/'pdx213-noble-full-candidate.tar.gz') as archive:
                self.assertNotIn('oem.img',archive.getnames())
                instructions=archive.extractfile('FLASHING.md').read()
                self.assertIn(b'checkout --detach '+b'a'*40,instructions)
                self.assertIn(b'--fastboot-output ./oem.img',instructions)
                self.assertIn(b'vbmeta_system_a',instructions)
                manifest=json.loads(archive.extractfile('candidate-manifest.json').read())
                self.assertEqual(manifest['artifacts']['FLASHING.md']['sha256'],hashlib.sha256(instructions).hexdigest())
                sums=archive.extractfile('SHA256SUMS').read().decode().splitlines()
                for line in sums:
                    digest,name=line.split('  ',1)
                    self.assertEqual(digest,hashlib.sha256(archive.extractfile(name).read()).hexdigest())

    def test_invalid_source_commit_cannot_enter_commands(self):
        for value in [None,'main','a'*39,'a'*40+'; echo bad']:
            with self.assertRaises(ValueError):flashing_instructions(False,value)

if __name__=='__main__':unittest.main()
