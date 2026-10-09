#!/usr/bin/env python3
"""Check the real generated archive's executable links before flashing."""
import argparse, gzip, os, subprocess, tempfile
from pathlib import Path
from build_standalone_boot import read_newc

def main():
    p=argparse.ArgumentParser();p.add_argument('ramdisk',type=Path);a=p.parse_args()
    records=read_newc(gzip.decompress(a.ramdisk.read_bytes()))
    def resolve(name):
        for _ in range(256):
            fields,data=records[name]
            if fields[1]&0o170000!=0o120000:return fields,data
            target=data.decode()
            name=os.path.normpath(target.lstrip('/') if target.startswith('/') else str(Path(name).parent/target))
        raise RuntimeError('Link cycle')
    shell=resolve('bin/sh')[1];bb=resolve('bin/busybox')[1]
    assert bb and shell==bb and bb[:4]==b'\x7fELF', 'Missing static BusyBox hard-link payload'
    assert records['init'][0][1]&0o111
    with tempfile.TemporaryDirectory() as tmp:
        binary=Path(tmp)/'busybox';binary.write_bytes(bb);binary.chmod(0o755)
        result=subprocess.check_output(['qemu-aarch64',str(binary),'sh','-c','printf rescue-shell-ok'],text=True)
        assert result=='rescue-shell-ok'
    print('Generated initramfs: BusyBox and shell resolve to working ARM64 executable')
if __name__=='__main__':main()
