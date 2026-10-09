#!/usr/bin/env python3
"""Build fixed-parameter Sony pdx213 boot images, without an installed OS backup."""
import argparse, gzip, hashlib, json, os, stat, struct, subprocess, sys
from pathlib import Path

def read_newc(data):
    result = {}
    pos = 0
    while data[pos:pos+6] in (b'070701', b'070702'):
        fields = [int(data[pos+6+i*8:pos+14+i*8],16) for i in range(13)]
        name = data[pos+110:pos+110+fields[11]-1].decode().removeprefix('./')
        start = (pos+110+fields[11]+3)&~3
        if name == 'TRAILER!!!': break
        result[name] = (fields, data[start:start+fields[6]])
        pos = (start+fields[6]+3)&~3
    return result

def archive(entries):
    out=bytearray()
    for number,(name,(mode,data)) in enumerate(entries.items(),1):
        encoded=name.encode()+b'\0'
        fields=[number,mode,0,0,1,0,len(data),0,0,0,0,len(encoded),0]
        out+=b'070701'+''.join(f'{v:08x}' for v in fields).encode()+encoded
        out+=b'\0'*(-len(out)%4); out+=data; out+=b'\0'*(-len(out)%4)
    name=b'TRAILER!!!\0'
    fields=[0,0,0,0,1,0,0,0,0,0,0,len(name),0]
    out+=b'070701'+''.join(f'{v:08x}' for v in fields).encode()+name
    out+=b'\0'*(-len(out)%512)
    return gzip.compress(out,mtime=0)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--base',type=Path,required=True)
    p.add_argument('--kernel',type=Path,required=True)
    p.add_argument('--metadata',type=Path,required=True)
    p.add_argument('--init',type=Path,required=True)
    p.add_argument('--extras',type=Path)
    p.add_argument('--mkbootimg',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    original=read_newc(gzip.decompress(a.base.read_bytes()))
    entries={n:(f[1],d) for n,(f,d) in original.items()}
    groups={}
    for name,(fields,data) in original.items():
        if stat.S_ISREG(fields[1]) and fields[4]>1:
            groups.setdefault((fields[0],fields[7],fields[8]),[]).append(name)
    for names in groups.values():
        canonical='bin/busybox' if 'bin/busybox' in names else next(n for n in names if original[n][1])
        payload=next(original[n][1] for n in names if original[n][1])
        entries[canonical]=(original[canonical][0][1],payload)
        for name in names:
            if name!=canonical: entries[name]=(0o120777,('/'+canonical).encode())
    # The Halium scripts are replaced completely. No original init can run.
    entries['init']=(0o100755,a.init.read_bytes())
    if a.extras:
        for path in sorted(a.extras.rglob('*')):
            name=str(path.relative_to(a.extras)); mode=path.lstat().st_mode
            data=os.readlink(path).encode() if path.is_symlink() else path.read_bytes() if stat.S_ISREG(mode) else b''
            entries[name]=(mode,data)
    ramdisk=a.output.with_suffix('.initrd.gz')
    ramdisk.write_bytes(archive(entries))
    metadata=json.loads(a.metadata.read_text())
    cmdline=metadata['cmdline']
    command=[sys.executable,str(a.mkbootimg),'--kernel',str(a.kernel),'--ramdisk',str(ramdisk)]
    for name in ['header_version','pagesize','base','kernel_offset','ramdisk_offset','second_offset','tags_offset']:
        command += ['--'+name,str(metadata[name])]
    subprocess.run(command+['--cmdline',cmdline,'--output',str(a.output)],check=True)
    data=a.output.read_bytes(); assert data[:8]==b'ANDROID!' and len(data)<96*1024*1024
    v=struct.unpack_from('<10I',data,8); assert v[7:9]==(4096,0)
    report={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),
      'kernel_sha256':hashlib.sha256(a.kernel.read_bytes()).hexdigest(),
      'base_ramdisk_sha256':hashlib.sha256(a.base.read_bytes()).hexdigest(),
      'init_sha256':hashlib.sha256(a.init.read_bytes()).hexdigest(),'cmdline':cmdline,
      'device_test':'pending'}
    a.output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
