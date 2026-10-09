#!/usr/bin/env python3
"""Assemble a local development userdata image; never fetch vendor, flash or publish."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from build import sha
from sources_lock import validate
ROOT=Path(__file__).resolve().parents[1]
def run(*args):subprocess.run([str(x) for x in args],check=True)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build-id',required=True)
    p.add_argument('--vendor',type=Path,required=True)
    for tool in ['mksquashfs','mke2fs','img2simg','avbtool']:p.add_argument('--'+tool,type=Path,required=True)
    a=p.parse_args()
    if not os.environ.get('FAKEROOTKEY'):p.error('Run the entire command under fakeroot to preserve archived ownership')
    if not os.environ.get('UT_PORTS_DATA_DIR'):p.error('UT_PORTS_DATA_DIR required')
    if Path(a.build_id).name!=a.build_id or a.build_id in ('.','..'):p.error('Safe build ID required')
    data=Path(os.environ['UT_PORTS_DATA_DIR']).resolve();build=data/'builds/pdx213'/a.build_id
    lock=validate(json.loads((ROOT/'sources.lock.json').read_text()),ROOT)['sources']
    if sha(a.vendor)!=lock['vendor']['sha256']:p.error('Unqualified vendor input hash')
    for name in ['rootfs','halium_gsi']:
        if sha(data/'downloads'/lock[name]['filename'])!=lock[name]['sha256']:p.error('Input hash mismatch: '+name)
    output=build/'userdata-package';output.mkdir(exist_ok=False)
    root=output/'rootfs';root.mkdir()
    run('tar','--same-owner','-xf',data/'downloads'/lock['rootfs']['filename'],'-C',root)
    run(sys.executable,ROOT/'tools/prepare_release_rootfs.py','--root',root,'--artifacts',build)
    run(sys.executable,ROOT/'tools/test_release_locale.py',root)
    stage=output/'stage';ut=stage/'utxperia';ut.mkdir(parents=True)
    for n in ['upper','work','userdata']:(ut/n).mkdir()
    (ut/'layout-version').write_text('1\n')
    run(a.mksquashfs,root,ut/'rootfs-ut24.squashfs','-comp','xz','-noappend','-no-progress','-processors','4')
    with (ut/'android-rootfs.img').open('wb') as f:
        subprocess.run(['tar','-xOf',str(data/'downloads'/lock['halium_gsi']['filename']),'system/var/lib/lxc/android/android-rootfs.img'],stdout=f,check=True)
    shutil.copyfile(a.vendor,ut/'vendor.img')
    for directory,dirs,files in os.walk(stage):
        os.chown(directory,0,0)
        for n in files:os.chown(Path(directory)/n,0,0)
    raw=output/'userdata.raw.img'
    with raw.open('wb') as f:f.truncate(3*1024**3)
    run(a.mke2fs,'-t','ext4','-F','-L','utxperia-data','-m','0','-b','4096','-O','^metadata_csum_seed,^orphan_file','-d',stage,raw)
    fill=output/'userdata.fill.img';run(a.img2simg,raw,fill)
    run(sys.executable,ROOT/'tools/sparse_raw_chunks.py',fill,output/'userdata.img')
    run(a.avbtool,'make_vbmeta_image','--output',output/'vbmeta.img','--flags','3','--algorithm','NONE')
    tools={name:{'sha256':sha(getattr(a,name))} for name in ['mksquashfs','mke2fs','img2simg','avbtool']}
    (output/'assembly-report.json').write_text(json.dumps({'scope':'local unqualified image assembly; no install/redistribution approval','tools':tools,'images':{n:sha(output/n) for n in ['userdata.img','vbmeta.img']}},indent=2)+'\n')
    print(output)
if __name__=='__main__':main()
