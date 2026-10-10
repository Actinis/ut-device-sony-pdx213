#!/usr/bin/env python3
"""Build the Noble kernel, DTBO, helpers and release boot from locked inputs."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
from sources_lock import validate
from dtbo_table import wrap
from build_manifest import sha, build_identity, write_report, prepare_build

ROOT=Path(__file__).resolve().parents[1]
def run(*args,**kw):subprocess.run([str(x) for x in args],check=True,**kw)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['kernel-source','ndk','mkbootimg-source']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--build-id',required=True)
    p.add_argument('--debugfs',type=Path,required=True,help='Host e2fsprogs debugfs executable')
    p.add_argument('--jobs',type=int,default=4)
    p.add_argument('--fetch-inputs',action='store_true')
    p.add_argument('--resume',action='store_true',help='Resume only the same source/input build in its existing output directory')
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
    expected_identity=build_identity(ROOT,a.build_id,lock)
    downloads=data/'downloads';downloads.mkdir(parents=True,exist_ok=True)
    for name in ['rootfs','initrd','halium_gsi']:
        entry=lock[name];target=downloads/entry['filename']
        if not target.exists() and a.fetch_inputs:
            tmp=target.with_suffix(target.suffix+'.part')
            with urllib.request.urlopen(entry['url']) as src,tmp.open('wb') as dest:shutil.copyfileobj(src,dest)
            if sha(tmp)!=entry['sha256']:tmp.unlink();raise SystemExit('Download hash mismatch: '+name)
            tmp.rename(target)
        if not target.exists() or sha(target)!=entry['sha256']:raise SystemExit('Missing or corrupt input: '+name)
    build=data/'builds/pdx213'/a.build_id
    prepare_build(build,expected_identity,a.resume)
    out=build/'out'
    toolbin=a.ndk.resolve()/'toolchains/llvm/prebuilt/linux-x86_64/bin'
    env=os.environ.copy();env['PATH']=str(toolbin)+os.pathsep+env['PATH'];env['TMPDIR']=str(build/'tmp');(build/'tmp').mkdir(exist_ok=a.resume)
    env['KBUILD_BUILD_VERSION']='1';env['KBUILD_BUILD_USER']='ut-ports';env['KBUILD_BUILD_HOST']='builder';env['KBUILD_BUILD_TIMESTAMP']='2026-10-09 00:00:00 UTC'
    kernel_out=build/'kernel';kernel_out.mkdir(exist_ok=a.resume)
    make=['make','-C',str(a.kernel_source.resolve()),'ARCH=arm64','O='+str(kernel_out),'LLVM=1','LLVM_IAS=1','CROSS_COMPILE=aarch64-linux-gnu-','CROSS_COMPILE_ARM32=arm-linux-gnueabi-']
    run(*make,'aosp_lena_pdx213_defconfig',env=env)
    run('bash',a.kernel_source/'scripts/kconfig/merge_config.sh','-m','-O',kernel_out,kernel_out/'.config',a.kernel_source/'arch/arm64/configs/pdx213_noble.config',env=env,cwd=a.kernel_source)
    run(*make,'olddefconfig',env=env)
    run(*make,'-j'+str(a.jobs),env=env)
    shutil.copy2(kernel_out/'arch/arm64/boot/Image.gz-dtb',out/'Image.gz-dtb')
    payload=(kernel_out/'arch/arm64/boot/dts/somc/lagoon-lena-pdx213_generic-overlay.dtbo').read_bytes()
    (out/'dtbo.img').write_bytes(wrap(payload))
    if (out/'modules').exists():shutil.rmtree(out/'modules')
    run(*make,'INSTALL_MOD_PATH='+str(out/'modules'),'INSTALL_MOD_STRIP=1','modules_install',env=env)
    for link in (out/'modules/lib/modules').glob('*/build'):
        if link.is_symlink():link.unlink()
    for link in (out/'modules/lib/modules').glob('*/source'):
        if link.is_symlink():link.unlink()
    clang=toolbin/'aarch64-linux-android30-clang'
    run(clang,'-nostdlib','-static','-Wl,-e,_start',ROOT/'device/reboot_bootloader.S','-o',out/'utxperia-reboot-bootloader')
    run(clang,'-shared','-fPIC','-O2',ROOT/'device/vndservicemanager-apparmor-compat.c','-o',out/'libvndservicemanager-apparmor-compat.so')
    ubuntu=build/'ubuntu';ubuntu.mkdir(exist_ok=a.resume)
    run('tar','--no-same-owner','-xf',downloads/lock['rootfs']['filename'],'-C',ubuntu)
    if 'VERSION_ID="24.04"' not in (ubuntu/'etc/os-release').read_text():raise SystemExit('Non-Noble rootfs rejected')
    android=build/'android-input';android.mkdir(exist_ok=a.resume)
    run('tar','--no-same-owner','-xf',downloads/lock['halium_gsi']['filename'],'-C',android)
    run(sys.executable,ROOT/'tools/build_gnss.py','--ndk',a.ndk,'--android-image',android/'system/var/lib/lxc/android/android-rootfs.img','--ubuntu-root',ubuntu,'--debugfs',a.debugfs,'--output',out/'gnss')
    run(sys.executable,ROOT/'tools/build_nfc.py','--ndk',a.ndk,'--android-image',android/'system/var/lib/lxc/android/android-rootfs.img','--ubuntu-root',ubuntu,'--debugfs',a.debugfs,'--work',build/'nfc','--output',out/'nfc','--downloads',downloads)
    run(sys.executable,ROOT/'tools/build_ofono.py','--ndk',a.ndk,'--ubuntu-root',ubuntu,'--work',build/'ofono','--output',out/'ofono','--downloads',downloads,'--jobs',a.jobs)
    run(sys.executable,ROOT/'tools/build_repowerd.py','--ndk',a.ndk,'--ubuntu-root',ubuntu,'--work',build/'repowerd','--output',out/'repowerd','--downloads',downloads,'--jobs',a.jobs)
    extras=build/'boot-extras'
    run(sys.executable,ROOT/'tools/stage_boot_filesystem.py','--ubuntu-root',ubuntu,'--reboot-helper',out/'utxperia-reboot-bootloader','--output',extras)
    run(sys.executable,ROOT/'tools/build_standalone_boot.py','--base',downloads/lock['initrd']['filename'],'--kernel',out/'Image.gz-dtb','--metadata',ROOT/'device/boot-metadata.json','--init',ROOT/'device/release-init','--extras',extras,'--mkbootimg',a.mkbootimg_source/'mkbootimg.py','--output',out/'boot.img')
    run(sys.executable,ROOT/'tools/test_standalone_boot.py',out/'boot.initrd.gz')
    run(sys.executable,ROOT/'tools/test_release_locale.py',ubuntu) if (ubuntu/'etc/locale.conf').read_text()=='LANG=en_US.UTF-8\n' else None
    write_report(build,expected_identity,(kernel_out/'include/config/kernel.release').read_text().strip())
    print('Built '+str(out))
if __name__=='__main__':main()
