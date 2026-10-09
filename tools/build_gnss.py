#!/usr/bin/env python3
"""Build public GNSS adaptation against the locked Android and Noble runtimes."""
import argparse
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LIBRARIES = ('libubuntu_application_api.so', 'libutils.so', 'liblog.so',
             'libhardware_legacy.so', 'libhidlbase.so',
             'android.hardware.gnss@1.0.so', 'android.hardware.gnss@1.1.so',
             'android.hardware.gnss@2.0.so', 'libc++.so')
INCLUDES = ('system/libhidl/base/include', 'system/libhidl/transport/include',
            'system/core/libutils/include', 'system/core/libcutils/include',
            'system/logging/liblog/include_vndk', 'system/core/libsystem/include',
            'hardware/libhardware_legacy/include', 'system/libhwbinder/include',
            'system/libfmq/base', 'system/libbase/include')

def run(*args):
    subprocess.run([str(arg) for arg in args], check=True)

def build(ndk, android_image, ubuntu_root, debugfs, output):
    output.mkdir(parents=True, exist_ok=True)
    link = output / 'link-inputs'
    link.mkdir(exist_ok=True)
    for name in LIBRARIES:
        dest = link / name
        # debugfs can return success after a failed command: verify every output.
        dest.unlink(missing_ok=True)
        run(debugfs, '-R', f'dump /system/lib64/{name} {dest}', android_image)
        if not dest.is_file() or dest.read_bytes()[:4] != b'\x7fELF':
            raise ValueError('Missing Android ELF input: ' + name)
    original = (link / 'libubuntu_application_api.so').read_bytes()
    old = b'libubuntu_application_api.so\0'
    replacement = b'libubuntu_application_old.so\0'
    if len(old) != len(replacement) or original.count(old) != 1:
        raise ValueError('Unexpected platform API SONAME; requalify GSI')
    (output / 'libubuntu_application_old.so').write_bytes(original.replace(old, replacement))
    source = ROOT / 'device/gnss'
    toolbin = ndk / 'toolchains/llvm/prebuilt/linux-x86_64/bin'
    includes = [source/'include/hidl', source/'include/api']
    includes += [source/'include/vndk'/path for path in INCLUDES]
    flags = [arg for path in includes for arg in ('-I', str(path))]
    obj = output / 'gnss.o'
    run(toolbin/'aarch64-linux-android30-clang++', '-std=c++17',
        '-D_LIBCPP_ABI_NAMESPACE=__1', '-fPIC', '-fno-rtti', '-O2',
        *flags, '-c', source/'gnss.cpp', '-o', obj)
    run(toolbin/'aarch64-linux-android30-clang++', '-shared', '-nostdlib++',
        '-Wl,-soname,libubuntu_application_api.so', obj, '-L'+str(link),
        '-L'+str(output), '-Wl,--no-as-needed', '-l:libubuntu_application_old.so',
        *['-l:'+name for name in LIBRARIES[1:]],
        '-o', output/'libubuntu_application_api.so')
    runtime = ubuntu_root/'lib/aarch64-linux-gnu'
    run(toolbin/'aarch64-linux-android30-clang', '-shared', '-nostdlib',
        '-fPIC', '-O2', '-fno-stack-protector', '-D_FORTIFY_SOURCE=0',
        '-I', source/'include/api', source/'assistance.c',
        runtime/'libc.so.6', runtime/'libdl.so.2',
        '-Wl,-soname,libutxperia-gnss-assistance.so',
        '-o', output/'libutxperia-gnss-assistance.so')
    obj.unlink()
    # Only deployable libraries belong in the build artifact inventory.
    import shutil
    shutil.rmtree(link)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('ndk','android-image','ubuntu-root','debugfs','output'):
        p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args()
    build(a.ndk.resolve(), a.android_image.resolve(), a.ubuntu_root.resolve(),
          a.debugfs.resolve(), a.output.resolve())

if __name__ == '__main__':
    main()
