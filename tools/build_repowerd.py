#!/usr/bin/env python3
"""Build the pinned Noble Repowerd adaptation in a fresh external directory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def run(*args, **kwargs):
    subprocess.run([str(a) for a in args], check=True, **kwargs)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def build(ndk, ubuntu, work, output, downloads, source_cache=None, jobs=4):
    from sources_lock import validate, validate_repowerd_inputs
    lock_path = ROOT / 'sources.lock.json'
    validate(json.loads(lock_path.read_text()), ROOT)
    base = ROOT / 'device/repowerd'
    inputs = validate_repowerd_inputs(json.loads((base / 'inputs.json').read_text()), base)
    runtime = ubuntu / 'usr/lib/aarch64-linux-gnu'
    # Pin the actual link-time runtime, not merely its directory name.
    libraries = {p.name: sha(p) for p in runtime.glob('*.so*') if p.is_file()}
    identity = {'inputs_sha256': sha(base / 'inputs.json'), 'lock_sha256': sha(lock_path),
                'builder_sha256': sha(Path(__file__)), 'runtime_libraries': libraries,
                'ndk_properties_sha256': sha(ndk / 'source.properties')}
    if work.is_symlink() or output.is_symlink():
        raise ValueError('Linked Repowerd directories rejected')
    report = output / 'repowerd-build-report.json'
    if report.is_file():
        saved = json.loads(report.read_text())
        binary = output / 'repowerd'
        if binary.is_symlink() or not binary.is_file() or saved.get('identity') != identity or saved.get('binary_sha256') != sha(binary):
            raise ValueError('Repowerd resume identity/artifact mismatch')
        return
    if work.exists() or output.exists():
        raise ValueError('Fresh Repowerd work/output directories required')
    if '23.1.7779620' not in (ndk / 'source.properties').read_text():
        raise ValueError('Locked NDK r23b required')
    work.mkdir(parents=True)
    output.mkdir(parents=True)
    downloads.mkdir(parents=True, exist_ok=True)
    source = work / 'source'
    origin = inputs['source']
    if source_cache:
        run('git', 'clone', '--shared', '--no-checkout', source_cache, source)
    else:
        run('git', 'init', source)
        run('git', '-C', source, 'fetch', '--depth=1', origin['url'], origin['commit'])
    run('git', '-C', source, 'checkout', '--detach', origin['commit'])
    if subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip() != origin['commit']:
        raise ValueError('Wrong Repowerd revision')
    run('git', '-C', source, 'apply', '--check', base / origin['patch'])
    run('git', '-C', source, 'apply', base / origin['patch'])
    harness = work / 'core-tests'
    harness.mkdir()
    shutil.copy2(base / 'core-tests.cmake', harness / 'CMakeLists.txt')
    with (output / 'core-tests.log').open('w') as log:
        run('cmake', '-S', harness, '-B', harness / 'out', '-DREPOWERD_SOURCE=' + str(source), stdout=log, stderr=subprocess.STDOUT)
        run('cmake', '--build', harness / 'out', '-j' + str(jobs), stdout=log, stderr=subprocess.STDOUT)
        run('ctest', '--test-dir', harness / 'out', '--output-on-failure', stdout=log, stderr=subprocess.STDOUT)
    sysroot = work / 'sysroot'
    sysroot.mkdir()
    for package in inputs['development_packages']:
        archive = downloads / package['filename']
        if not archive.exists():
            partial = archive.with_suffix('.part')
            with urllib.request.urlopen(package['url']) as src, partial.open('wb') as dst:
                shutil.copyfileobj(src, dst)
            if sha(partial) != package['sha256']:
                partial.unlink()
                raise ValueError('Repowerd package download hash mismatch')
            partial.rename(archive)
        if sha(archive) != package['sha256']:
            raise ValueError('Repowerd cached package hash mismatch')
        members = subprocess.check_output(['ar', 't', str(archive)], text=True).splitlines()
        member = next(name for name in members if name.startswith('data.tar.'))
        tar = work / member
        tar.write_bytes(subprocess.check_output(['ar', 'p', str(archive), member]))
        run('tar', '-xf', tar, '-C', sysroot)
        tar.unlink()
    dest = sysroot / 'usr/lib/aarch64-linux-gnu'
    for p in runtime.glob('*.so*'):
        if p.is_file():
            target = dest / p.name
            target.unlink(missing_ok=True)
            target.symlink_to(p.resolve())
    # Development package symlinks can refer to an older SONAME file; link
    # against the locked rootfs runtime instead. GNU ld scripts stay local.
    for name, soname in {'deviceinfo': 'libdeviceinfo.so.0', 'hybris-common': 'libhybris-common.so.1',
                         'android-properties': 'libandroid-properties.so.1', 'gbinder': 'libgbinder.so.1',
                         'glibutil': 'libglibutil.so.1', 'glib-2.0': 'libglib-2.0.so.0',
                         'gobject-2.0': 'libgobject-2.0.so.0', 'gio-2.0': 'libgio-2.0.so.0',
                         'stdc++': 'libstdc++.so.6'}.items():
        if not (runtime / soname).is_file():
            raise ValueError('Missing locked runtime: ' + soname)
        target = dest / ('lib' + name + '.so')
        target.unlink(missing_ok=True)
        target.symlink_to(soname)
    (sysroot / 'lib').symlink_to('usr/lib')
    (sysroot / 'usr/lib/ld-linux-aarch64.so.1').symlink_to('aarch64-linux-gnu/ld-linux-aarch64.so.1')
    toolbin = ndk / 'toolchains/llvm/prebuilt/linux-x86_64/bin'
    toolchain = work / 'cross.cmake'
    toolchain.write_text(f'''set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)
set(CMAKE_SYSROOT "{sysroot}")
set(CMAKE_C_COMPILER "{toolbin}/clang")
set(CMAKE_CXX_COMPILER "{toolbin}/clang++")
set(CMAKE_C_COMPILER_TARGET aarch64-linux-gnu)
set(CMAKE_CXX_COMPILER_TARGET aarch64-linux-gnu)
set(CMAKE_C_FLAGS_INIT "--gcc-toolchain={sysroot}/usr -Wno-unused-command-line-argument -B{dest}")
set(CMAKE_CXX_FLAGS_INIT "--gcc-toolchain={sysroot}/usr -Wno-unused-command-line-argument -B{dest} -stdlib=libstdc++")
set(CMAKE_EXE_LINKER_FLAGS_INIT "-fuse-ld=lld -L{dest} -Wl,-rpath-link,{dest}")
set(CMAKE_FIND_ROOT_PATH "{sysroot}")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
''')
    env = os.environ.copy()
    env['PKG_CONFIG_SYSROOT_DIR'] = str(sysroot)
    env['PKG_CONFIG_LIBDIR'] = str(dest / 'pkgconfig') + os.pathsep + str(sysroot / 'usr/share/pkgconfig')
    cmake_out = work / 'cmake'
    with (work / 'build.log').open('w') as log:
        run('cmake', '-S', source, '-B', cmake_out, '-DCMAKE_TOOLCHAIN_FILE=' + str(toolchain),
            '-DREPOWERD_BUILD_TESTS=OFF', '-DENABLE_WERROR=OFF', '-DCMAKE_BUILD_TYPE=Release',
            '-DCMAKE_INSTALL_PREFIX=/usr', env=env, stdout=log, stderr=subprocess.STDOUT)
        run('cmake', '--build', cmake_out, '--target', 'repowerd', '-j' + str(jobs),
            env=env, stdout=log, stderr=subprocess.STDOUT)
    binary = output / 'repowerd'
    shutil.copy2(cmake_out / 'bin/repowerd', binary)
    if binary.read_bytes()[:5] != b'\x7fELF\x02':
        raise ValueError('Missing ARM64 Repowerd output')
    report.write_text(json.dumps({'identity': identity, 'base_commit': origin['commit'],
                                 'patch_sha256': origin['patch_sha256'], 'core_tests': 'passed (host; excludes performance-booster target)', 'binary_sha256': sha(binary)}, indent=2) + '\n')
    print('Built locked ARM64 Repowerd: ' + str(binary))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('ndk', 'ubuntu-root', 'work', 'output', 'downloads'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--source-cache', type=Path, help='Optional Git object cache; exact revision still checked')
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error('Positive job count required')
    build(args.ndk.resolve(), args.ubuntu_root.resolve(), args.work.resolve(), args.output.resolve(),
          args.downloads.resolve(), args.source_cache, args.jobs)


if __name__ == '__main__':
    main()
