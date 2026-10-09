#!/usr/bin/env python3
"""Build the Noble kernel, DTBO, helpers and release boot from locked inputs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
from sources_lock import validate

ROOT=Path(__file__).resolve().parents[1]
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def run(*args,**kw):subprocess.run([str(x) for x in args],check=True,**kw)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['kernel-source','ndk','mkbootimg-source']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--build-id',required=True)
    p.add_argument('--jobs',type=int,default=4)
    p.add_argument('--fetch-inputs',action='store_true')
    a=p.parse_args()
    if not a.build_id or Path(a.build_id).name!=a.build_id or a.build_id in ('.','..'):p.error('Safe build ID required')
    if a.jobs<1:p.error('Positive job count required')
    if not os.environ.get('UT_PORTS_DATA_DIR'):p.error('Set UT_PORTS_DATA_DIR explicitly')
    data=Path(os.environ['UT_PORTS_DATA_DIR']).resolve()
    lock=validate(json.loads((ROOT/'sources.lock.json').read_text()),ROOT)['sources']
    for name,path in [('kernel',a.kernel_source),('mkbootimg',a.mkbootimg_source)]:
        commit=subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()
        if commit!=lock[name]['commit']:raise SystemExit('Wrong '+name+' commit')
        if subprocess.check_output(['git','-C',str(path),'status','--porcelain'],text=True):raise SystemExit('Dirty source: '+name)
    if '23.1.7779620' not in (a.ndk/'source.properties').read_text():raise SystemExit('NDK r23b required')
    downloads=data/'downloads';downloads.mkdir(parents=True,exist_ok=True)
    for name in ['rootfs','initrd']:
        entry=lock[name];target=downloads/entry['filename']
        if not target.exists() and a.fetch_inputs:
            tmp=target.with_suffix(target.suffix+'.part')
            with urllib.request.urlopen(entry['url']) as src,tmp.open('wb') as dest:shutil.copyfileobj(src,dest)
            if sha(tmp)!=entry['sha256']:tmp.unlink();raise SystemExit('Download hash mismatch: '+name)
            tmp.rename(target)
        if not target.exists() or sha(target)!=entry['sha256']:raise SystemExit('Missing or corrupt input: '+name)
    build=data/'builds/pdx213'/a.build_id
    build.mkdir(parents=True,exist_ok=False)
    out=build/'out';out.mkdir()
    toolbin=a.ndk.resolve()/'toolchains/llvm/prebuilt/linux-x86_64/bin'
    env=os.environ.copy();env['PATH']=str(toolbin)+os.pathsep+env['PATH'];env['TMPDIR']=str(build/'tmp');(build/'tmp').mkdir()
    env['KBUILD_BUILD_USER']='ut-ports';env['KBUILD_BUILD_HOST']='builder';env['KBUILD_BUILD_TIMESTAMP']='2026-10-09 00:00:00 UTC'
    kernel_out=build/'kernel';kernel_out.mkdir()
    make=['make','-C',str(a.kernel_source.resolve()),'ARCH=arm64','O='+str(kernel_out),'LLVM=1','LLVM_IAS=1','CROSS_COMPILE=aarch64-linux-gnu-','CROSS_COMPILE_ARM32=arm-linux-gnueabi-']
    run(*make,'aosp_lena_pdx213_defconfig',env=env)
    run('bash',a.kernel_source/'scripts/kconfig/merge_config.sh','-m','-O',kernel_out,kernel_out/'.config',a.kernel_source/'arch/arm64/configs/pdx213_noble.config',env=env,cwd=a.kernel_source)
    run(*make,'olddefconfig',env=env)
    run(*make,'-j'+str(a.jobs),env=env)
    for src,name in [('Image.gz-dtb','Image.gz-dtb'),('dtbo.img','dtbo.img')]:shutil.copy2(kernel_out/'arch/arm64/boot'/src,out/name)
    clang=toolbin/'aarch64-linux-android30-clang'
    run(clang,'-nostdlib','-static','-Wl,-e,_start',ROOT/'device/reboot_bootloader.S','-o',out/'utxperia-reboot-bootloader')
    run(clang,'-shared','-fPIC','-O2',ROOT/'device/vndservicemanager-apparmor-compat.c','-o',out/'libvndservicemanager-apparmor-compat.so')
    ubuntu=build/'ubuntu';ubuntu.mkdir()
    run('tar','--no-same-owner','-xf',downloads/lock['rootfs']['filename'],'-C',ubuntu)
    if 'VERSION_ID="24.04"' not in (ubuntu/'etc/os-release').read_text():raise SystemExit('Non-Noble rootfs rejected')
    extras=build/'boot-extras'
    run(sys.executable,ROOT/'tools/stage_boot_filesystem.py','--ubuntu-root',ubuntu,'--reboot-helper',out/'utxperia-reboot-bootloader','--output',extras)
    run(sys.executable,ROOT/'tools/build_standalone_boot.py','--base',downloads/lock['initrd']['filename'],'--kernel',out/'Image.gz-dtb','--metadata',ROOT/'device/boot-metadata.json','--init',ROOT/'device/release-init','--extras',extras,'--mkbootimg',a.mkbootimg_source/'mkbootimg.py','--output',out/'boot.img')
    run(sys.executable,ROOT/'tools/test_standalone_boot.py',out/'boot.initrd.gz')
    run(sys.executable,ROOT/'tools/test_release_locale.py',ubuntu) if (ubuntu/'etc/locale.conf').read_text()=='LANG=en_US.UTF-8\n' else None
    report={'scope':'kernel, DTBO, helper libraries and boot; no full userdata or hardware qualification','device_commit':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),'sources':lock,'artifacts':{f.name:sha(f) for f in out.iterdir() if f.is_file()}}
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Built '+str(out))
if __name__=='__main__':main()
