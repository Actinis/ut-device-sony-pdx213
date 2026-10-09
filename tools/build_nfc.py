#!/usr/bin/env python3
"""Build the locked SN100/Classic NFC stack outside the source checkout."""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ARTIFACTS=('nfcd','binder.so','libncicore.so.1','libnciplugin.so.1','nfc_nci_nxp.so','vendor.nxp.nxpese@1.0.so')
def run(*args,**kwargs):subprocess.run([str(x) for x in args],check=True,**kwargs)
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def extract_elf(debugfs,image,path,dest):
 dest.unlink(missing_ok=True);run(debugfs,'-R',f'dump {path} {dest}',image)
 if not dest.is_file() or dest.read_bytes()[:5]!=b'\x7fELF\x02':raise ValueError('Missing ARM64 linker input: '+path)
def runtime_identity(ndk, image, ubuntu):
 runtime=ubuntu/'usr/lib/aarch64-linux-gnu'
 names=('libglibutil.so.1','libgobject-2.0.so.0','libglib-2.0.so.0','libc.so.6',
        'libgbinder.so.1','libnfcdef.so.1','libgio-2.0.so.0','libdl.so.2','ld-linux-aarch64.so.1')
 return {'android_image_sha256':digest(image),
         'ubuntu_libraries':{n:digest(runtime/n) for n in names},
         'ndk_properties_sha256':digest(ndk/'source.properties'),
         'builder_sha256':digest(Path(__file__))}

def build(ndk,image,ubuntu,debugfs,work,out,downloads,source_cache=None):
 source=ROOT/'device/nfc';inputs=json.loads((source/'inputs.json').read_text())
 from sources_lock import validate, validate_nfc_inputs
 validate(json.loads((ROOT/'sources.lock.json').read_text()),ROOT);validate_nfc_inputs(inputs,source)
 identity=runtime_identity(ndk,image,ubuntu)
 if out.is_symlink() or work.is_symlink():raise ValueError('Linked NFC build directories rejected')
 report=out/'nfc-build-report.json'
 if report.is_file():
  saved=json.loads(report.read_text())
  if any((out/name).is_symlink() or not (out/name).is_file() for name in ARTIFACTS):raise ValueError('Missing or linked NFC artifact')
  expected={name:digest(out/name) for name in ARTIFACTS}
  if saved.get('runtime_identity')!=identity or saved.get('inputs_sha256')!=digest(source/'inputs.json') or saved.get('lock_sha256')!=digest(ROOT/'sources.lock.json') or saved.get('artifacts')!=expected:raise ValueError('NFC resume identity/artifact mismatch')
  return
 if work.exists() or out.exists():raise ValueError('Fresh NFC work/output directories required for an incomplete build')
 work.mkdir(parents=True);out.mkdir(parents=True);downloads.mkdir(parents=True,exist_ok=True)
 repos={}
 for e in inputs['sources']:
  name=e['component'];dest=work/name
  if source_cache and (source_cache/name/'.git').exists():run('git','clone','--shared','--no-checkout',source_cache/name,dest)
  else:
   run('git','init',dest);run('git','-C',dest,'fetch','--depth=1',e['url'],e['commit'])
  run('git','-C',dest,'checkout','--detach',e['commit'])
  if subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip()!=e['commit']:raise ValueError('Wrong source commit')
  if 'patch' in e:
   patch=source/e['patch']
   if digest(patch)!=e['patch_sha256']:raise ValueError('Patch hash mismatch')
   run('git','-C',dest,'apply','--check',patch);run('git','-C',dest,'apply',patch)
  repos[name]=dest
 sysroot=work/'sysroot';sysroot.mkdir()
 for e in inputs['development_headers']:
  archive=downloads/e['filename']
  if not archive.exists():
   tmp=archive.with_suffix('.part')
   with urllib.request.urlopen(e['url']) as src,tmp.open('wb') as dst:shutil.copyfileobj(src,dst)
   if digest(tmp)!=e['sha256']:tmp.unlink();raise ValueError('Package hash mismatch')
   tmp.rename(archive)
  if digest(archive)!=e['sha256']:raise ValueError('Cached package hash mismatch')
  members=subprocess.check_output(['ar','t',str(archive)],text=True).splitlines()
  member=next(x for x in members if x.startswith('data.tar.'))
  tar=work/member;tar.write_bytes(subprocess.check_output(['ar','p',str(archive),member]));run('tar','-xf',tar,'-C',sysroot);tar.unlink()
 toolbin=ndk/'toolchains/llvm/prebuilt/linux-x86_64/bin'
 if '23.1.7779620' not in (ndk/'source.properties').read_text():raise ValueError('Locked NDK r23b required')
 linuxcc=toolbin/'clang';androidcc=toolbin/'aarch64-linux-android30-clang++'
 inc=sysroot/'usr/include';runtime=ubuntu/'usr/lib/aarch64-linux-gnu'
 cflags=['--target=aarch64-linux-gnu','--sysroot='+str(sysroot),'-mno-outline-atomics','-fPIC','-O2','-DDEBUG','-DDISABLE_HEXDUMP','-Werror=implicit-function-declaration']
 includes=[repos['nfcd']/'core/include',repos['nci-plugin']/'include',repos['ncicore']/'include',inc,inc/'aarch64-linux-gnu',inc/'glib-2.0',sysroot/'usr/lib/aarch64-linux-gnu/glib-2.0/include',inc/'gbinder',inc/'gutil',inc/'nfcd',inc/'nciplugin',inc/'ncicore',inc/'nfcdef',inc/'gio-unix-2.0']
 cflags += [arg for p in includes for arg in ('-I',str(p))]
 def shared(name,files,libs,extra=()):
  obj=work/(name+'-obj');obj.mkdir();objects=[]
  for p in files:
   o=obj/(p.stem+'.o');run(linuxcc,*cflags,*extra,'-c',p,'-o',o);objects.append(o)
  run(linuxcc,'--target=aarch64-linux-gnu','-fuse-ld=lld','-shared','-nostdlib','-Wl,-soname,'+name,'-Wl,-rpath-link,'+str(runtime),*objects,*[runtime/n for n in libs],'-o',out/name)
 shared('libncicore.so.1',sorted((repos['ncicore']/'src').glob('*.c')),['libglibutil.so.1','libgobject-2.0.so.0','libglib-2.0.so.0','libc.so.6'])
 shared('libnciplugin.so.1',sorted((repos['nci-plugin']/'src').glob('*.c')),['libncicore.so.1','libglibutil.so.1','libgobject-2.0.so.0','libglib-2.0.so.0','libc.so.6'])
 shared('binder.so',sorted((repos['binder-plugin']/'src').glob('*.c')),['libncicore.so.1','libnciplugin.so.1','libgbinder.so.1','libglibutil.so.1','libgobject-2.0.so.0','libglib-2.0.so.0','libc.so.6'],('-fvisibility=hidden','-DNFC_PLUGIN_EXTERNAL'))
 # Use portable Python codegen from the locked Noble package, never host GLib.
 env=os.environ.copy();env['PATH']=str(sysroot/'usr/bin')+os.pathsep+str(toolbin)+os.pathsep+env['PATH']
 env['PKG_CONFIG_SYSROOT_DIR']=str(sysroot);env['PKG_CONFIG_LIBDIR']=str(sysroot/'usr/lib/aarch64-linux-gnu/pkgconfig')
 link=work/'linux-link';link.mkdir()
 for name in ['libnfcdef','libglibutil','libgio-2.0','libgobject-2.0','libglib-2.0','libdl','libc']:
  choices=sorted(runtime.glob(name+'.so.*'))
  if not choices:raise ValueError('Missing Noble runtime: '+name)
  (link/(name+'.so')).symlink_to(choices[0])
 cc=' '.join([str(linuxcc),*cflags]);startup=sysroot/'usr/lib/aarch64-linux-gnu'
 ld=cc+' -fuse-ld=lld -nostdlib '+str(startup/'Scrt1.o')+' '+str(startup/'crti.o')
 options=['CC='+cc,'LD='+ld,'AR='+str(toolbin/'llvm-ar'),'HAVE_DBUSACCESS=0','KEEP_SYMBOLS=1','CFLAGS='+' '.join(cflags),'LDFLAGS=-L'+str(link)+' -Wl,-rpath-link,'+str(runtime),'LIBDIR=/usr/lib','LIBS='+' '.join(str(p) for p in link.glob('*.so'))+' '+str(runtime/'ld-linux-aarch64.so.1')+' '+str(startup/'crtn.o')]
 run('make','-j4','-C',repos['nfcd']/'src','debug',*options,env=env)
 shutil.copy2(repos['nfcd']/'src/build/debug/nfcd',out/'nfcd')
 symbols=subprocess.check_output([str(toolbin/'llvm-nm'),'--defined-only',str(out/'nfcd')],text=True)
 for name in ('dbus_handlers','dbus_neard','dbus_service','settings'):
  if not any(line.split()[-1]=='_nfc_plugin_'+name for line in symbols.splitlines()):
   raise ValueError('Missing builtin NFC plugin: '+name)
 symbols=subprocess.check_output([str(toolbin/'llvm-nm'),'--defined-only',str(out/'binder.so')],text=True)
 if not any(line.split()[-1]=='nfc_plugin_desc' for line in symbols.splitlines()):raise ValueError('Missing external binder plugin descriptor')

 # Execute the shipped synthetic Classic regression suite using locked ARM64
 # libraries. Its executable/log stay in work, outside installation artifacts.
 testobj=work/'classic-test-obj';testobj.mkdir();objects=[]
 for p in (repos['nfcd']/'unit/core_tag_mfc/test_core_tag_mfc.c',repos['nfcd']/'unit/common/test_target.c'):
  o=testobj/(p.stem+'.o')
  run(linuxcc,*cflags,'-I'+str(repos['nfcd']/'core/src'),'-I'+str(repos['nfcd']/'unit/common'),'-c',p,'-o',o);objects.append(o)
 test=work/'test-core-tag-mfc'
 run(linuxcc,'--target=aarch64-linux-gnu','-fuse-ld=lld','-nostdlib','-pie',
     startup/'Scrt1.o',startup/'crti.o',*objects,repos['nfcd']/'core/build/debug/libnfc-core.a',
     *[runtime/n for n in ('libnfcdef.so.1','libglibutil.so.1','libgobject-2.0.so.0','libgio-2.0.so.0','libglib-2.0.so.0','libc.so.6','ld-linux-aarch64.so.1')],
     '-Wl,-rpath-link,'+str(runtime),startup/'crtn.o','-o',test)
 with (work/'classic-tests.log').open('w') as log:
  run('qemu-aarch64','-L',ubuntu,test,stdout=log,stderr=subprocess.STDOUT)
 print((work/'classic-tests.log').read_text())

 # Link only against the official locked GSI, not a connected phone.
 android_link=work/'android-link';android_link.mkdir()
 libs=['android.hardware.nfc@1.0.so','android.hardware.nfc@1.1.so','android.hardware.nfc@1.2.so','android.hardware.secure_element@1.0.so','libbase.so','libcutils.so','libhardware.so','libhardware_legacy.so','libhidlbase.so','liblog.so','libutils.so','libc++.so']
 for name in libs:
  path='/system/lib64/' if name=='liblog.so' else '/system/apex/com.android.vndk.current/lib64/'
  extract_elf(debugfs,image,path+name,android_link/name)
 h=repos['hal']/'SN100x';vndk_paths=['system/libhidl/base/include','system/libhidl/transport/include','system/core/libutils/include','system/core/libcutils/include','system/logging/liblog/include_vndk','system/core/libsystem/include','hardware/libhardware/include','hardware/libhardware_legacy/include','system/libhwbinder/include','system/libfmq/base','system/libbase/include']
 includes=[source/'include/hidl',ROOT/'device/gnss/include/hidl',repos['ese-extns']/'inc',repos['hal'],repos['ese-nxp']/'extns/impl',repos['ese']/'halimpl/inc',h/'extns/impl/nxpnfc/2.0']+[p for p in (h/'halimpl').rglob('*') if p.is_dir()]
 includes += [root/'include/vndk'/p for root in (source,ROOT/'device/gnss') for p in vndk_paths]
 flags=['-std=c++17','-D_LIBCPP_ABI_NAMESPACE=__1','-fPIC','-O2','-DNXP_EXTNS=TRUE','-DNXP_HW_SELF_TEST=TRUE','-DNXP_SRD=TRUE','-DPH_LIBNFC_ENABLE_FORCE_DOWNLOAD=0','-DNXP_QTAG=TRUE']+['-I'+str(p) for p in includes]
 obj=work/'android-obj';obj.mkdir()
 def compile_cpp(p):
  o=obj/(hashlib.sha256(str(p).encode()).hexdigest()+'.o');run(androidcc,*flags,'-fno-rtti','-c',p,'-o',o);return o
 ese=[compile_cpp(p) for p in sorted((source/'hidl/vendor/nxp/nxpese/1.0').glob('*.cpp'))]
 run(androidcc,'-shared','-nostdlib++','-Wl,--no-undefined','-Wl,-soname,vendor.nxp.nxpese@1.0.so',*ese,'-L'+str(android_link),*['-l:'+p for p in ['libhidlbase.so','libutils.so','liblog.so','libcutils.so','libc++.so']],'-o',out/'vendor.nxp.nxpese@1.0.so')
 sources=[];block=(h/'Android.bp').read_text().split('srcs: [',1)[1].split('],',1)[0]
 for pattern in re.findall(r'"([^\"]+\.cc)"',block):sources+=sorted(h.glob(pattern))
 objects=[compile_cpp(p) for p in sources]+[compile_cpp(p) for p in sorted((source/'hidl/vendor/nxp/nxpnfc/2.0').glob('*.cpp'))]
 run(androidcc,'-shared','-nostdlib++','-Wl,--no-undefined','-Wl,-soname,nfc_nci_nxp.so',*objects,'-L'+str(android_link),'-L'+str(out),'-Wl,--no-as-needed',*['-l:'+p for p in libs],'-l:vendor.nxp.nxpese@1.0.so','-o',out/'nfc_nci_nxp.so')
 for name in ARTIFACTS:
  p=out/name
  if p.read_bytes()[:5]!=b'\x7fELF\x02':raise ValueError('Missing ARM64 NFC output: '+name)
 (out/'nfc-build-report.json').write_text(json.dumps({'runtime_identity':identity,'inputs_sha256':digest(source/'inputs.json'),'lock_sha256':digest(ROOT/'sources.lock.json'),'tests':{'classic_reader_writer':'passed under ARM64 QEMU; synthetic data'},'artifacts':{name:digest(out/name) for name in ARTIFACTS}},indent=2)+'\n')
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['ndk','android-image','ubuntu-root','debugfs','work','output','downloads']:p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--source-cache',type=Path,help='Optional Git object cache; revisions still verified')
 a=p.parse_args();build(a.ndk.resolve(),a.android_image.resolve(),a.ubuntu_root.resolve(),a.debugfs.resolve(),a.work.resolve(),a.output.resolve(),a.downloads.resolve(),a.source_cache)
if __name__=='__main__':main()
