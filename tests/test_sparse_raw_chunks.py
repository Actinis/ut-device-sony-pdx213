import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
spec=importlib.util.spec_from_file_location('sparse',Path(__file__).resolve().parents[1]/'tools/sparse_raw_chunks.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class Sparse(unittest.TestCase):
    def fixture(self):
        header=struct.pack('<IHHHHIIII',0xed26ff3a,1,0,28,12,4096,4,3,0)
        raw=b'A'*4096
        return header+struct.pack('<HHII',0xcac1,0,1,4108)+raw+struct.pack('<HHII',0xcac2,0,2,16)+b'\x12\x34\x56\x78'+struct.pack('<HHII',0xcac3,0,1,12)
    def test_fill_becomes_raw_with_identical_virtual_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'source';dest=Path(tmp)/'dest';source.write_bytes(self.fixture())
            module.convert(source,dest)
            blob=dest.read_bytes();header=struct.unpack_from('<IHHHHIIII',blob)
            self.assertEqual(header[6],4)
            position=28;content=bytearray()
            for _ in range(header[7]):
                kind,_,blocks,total=struct.unpack_from('<HHII',blob,position)
                self.assertNotEqual(kind,0xcac2)
                payload=blob[position+12:position+total]
                content.extend(payload if kind==0xcac1 else bytes(blocks*4096))
                position+=total
            self.assertEqual(position,len(blob))
            self.assertEqual(content,b'A'*4096+b'\x12\x34\x56\x78'*2048+bytes(4096))
    def test_truncation_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'source';dest=Path(tmp)/'dest';source.write_bytes(self.fixture()[:-1])
            with self.assertRaises(ValueError):module.convert(source,dest)
