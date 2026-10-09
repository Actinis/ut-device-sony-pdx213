#!/usr/bin/env python3
"""Prepare filesystem tools from an extracted official Ubuntu ARM64 rootfs."""
import argparse, os, re, shutil, subprocess
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--ubuntu-root',type=Path,required=True)
    
    
    p.add_argument('--reboot-helper',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); root=a.ubuntu_root.resolve(); out=a.output
    out.mkdir(parents=True,exist_ok=True)
    def resolve(name):
        parts=[]
        pending=name.lstrip('/').split('/')
        for _ in range(256):
            if not pending:return root.joinpath(*parts)
            part=pending.pop(0)
            if part in ('','.') :continue
            if part=='..':
                if parts:parts.pop()
                continue
            candidate=root.joinpath(*parts,part)
            if candidate.is_symlink():
                target=os.readlink(candidate)
                if target.startswith('/'):parts=[]
                pending=target.split('/')+pending
            else:parts.append(part)
        raise SystemExit('Symlink loop in Ubuntu root')
    seen=set()
    def copy(name):
        if name in seen:return
        seen.add(name); source=resolve(name)
        destination=out/name.lstrip('/'); destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,destination); shutil.copymode(source,destination)
        if source.read_bytes()[:4]!=b'\x7fELF':return
        dynamic=subprocess.check_output(['readelf','-d',str(source)],text=True)
        for lib in re.findall(r'\(NEEDED\).*?\[(.*?)\]',dynamic):
            paths=['/lib/aarch64-linux-gnu/'+lib,'/usr/lib/aarch64-linux-gnu/'+lib]
            name=next((v for v in paths if resolve(v).is_file()),None)
            if name is None:raise SystemExit('Missing dependency '+lib)
            copy(name)
        segments=subprocess.check_output(['readelf','-l',str(source)],text=True)
        for loader in re.findall(r'Requesting program interpreter: (.*?)\]',segments):copy(loader)
    names=['/usr/sbin/resize2fs','/usr/sbin/e2fsck','/usr/sbin/blkid','/etc/mke2fs.conf']
    for name in names:copy(name)
    path=out/'bin/utxperia-reboot-bootloader';path.parent.mkdir(exist_ok=True)
    shutil.copyfile(a.reboot_helper,path);path.chmod(0o755)
    print(f'Prepared {len(seen)} filesystem tools and dependencies')
if __name__=='__main__':main()
