#!/usr/bin/env python3
"""Build the pinned Noble Qt camera plugin and its ARM64 cancellation check."""
import argparse
import concurrent.futures
import json
from pathlib import Path
import shutil
import subprocess
import urllib.request
from build_repowerd import run, sha

ROOT = Path(__file__).resolve().parents[1]
LIBRARIES = ['libEGL.so.1', 'libui.so.1', 'libexiv2.so.27', 'libqtubuntu-media-signals.so.2',
             'libQt5Gui.so.5', 'libQt5Core.so.5', 'libmedia.so.1', 'libcamera.so.1',
             'libhybris-common.so.1', 'libpulse-simple.so.0', 'libpulse.so.0',
             'libandroid-properties.so.1', 'libdeviceinfo.so.0', 'libQt5Multimedia.so.5',
             'libQt5Sensors.so.5', 'libGLESv2.so.2']


def artifacts(output):
    result = {p.relative_to(output).as_posix(): sha(p) for p in output.rglob('*')
              if p.is_file() and p.name != 'camera-build-report.json'}
    if set(result) != {'libaalcamera.so', 'fifo-cancel.log', 'licences/COPYING'}:
        raise ValueError('Missing or unexpected camera build artifacts')
    return result


def build(ndk, ubuntu, work, output, downloads, qemu, source_cache=None, jobs=4):
    from sources_lock import validate, validate_camera_inputs
    lock_path = ROOT / 'sources.lock.json'
    validate(json.loads(lock_path.read_text()), ROOT)
    base = ROOT / 'device/camera'
    inputs = validate_camera_inputs(json.loads((base / 'inputs.json').read_text()), base)
    runtime = ubuntu / 'usr/lib/aarch64-linux-gnu'
    original = runtime / 'qt5/plugins/mediaservice/libaalcamera.so'
    if not original.is_file() or sha(original) != inputs['original_plugin_sha256']:
        raise ValueError('Wrong Noble camera plugin baseline')
    identity = {'inputs_sha256': sha(base / 'inputs.json'), 'lock_sha256': sha(lock_path),
                'builder_sha256': sha(Path(__file__)), 'ndk_properties_sha256': sha(ndk / 'source.properties'),
                'runtime_libraries': {p.name: sha(p) for p in runtime.glob('*.so*') if p.is_file()},
                'qemu_sha256': sha(qemu),
                'qemu_version': subprocess.check_output([str(qemu), '--version'], text=True).splitlines()[0]}
    if work.is_symlink() or output.is_symlink():
        raise ValueError('Linked camera directories rejected')
    report = output / 'camera-build-report.json'
    if report.is_file():
        saved = json.loads(report.read_text())
        if saved.get('identity') != identity or saved.get('artifacts') != artifacts(output):
            raise ValueError('Camera resume identity/artifact mismatch')
        return
    if work.exists() or output.exists():
        raise ValueError('Fresh camera work/output directories required')
    if '23.1.7779620' not in (ndk / 'source.properties').read_text():
        raise ValueError('Locked NDK r23b required')
    work.mkdir(parents=True); output.mkdir(parents=True); downloads.mkdir(parents=True, exist_ok=True)
    source = work / 'source'; origin = inputs['source']
    if source_cache:
        run('git', 'clone', '--shared', '--no-checkout', source_cache, source)
    else:
        run('git', 'init', source)
        run('git', '-C', source, 'fetch', '--depth=1', origin['url'], origin['commit'])
    run('git', '-C', source, 'checkout', '--detach', origin['commit'])
    run('git', '-C', source, 'apply', '--check', base / origin['patch'])
    run('git', '-C', source, 'apply', base / origin['patch'])
    sysroot = work / 'sysroot'; sysroot.mkdir()
    for package in inputs['development_packages']:
        archive = downloads / package['filename']
        if not archive.exists():
            partial = archive.with_suffix('.part')
            with urllib.request.urlopen(package['url']) as src, partial.open('wb') as dst:
                shutil.copyfileobj(src, dst)
            if sha(partial) != package['sha256']:
                partial.unlink(); raise ValueError('Camera package download hash mismatch')
            partial.replace(archive)
        if sha(archive) != package['sha256']:
            raise ValueError('Camera cached package hash mismatch')
        member = next(n for n in subprocess.check_output(['ar', 't', str(archive)], text=True).splitlines()
                      if n.startswith('data.tar.'))
        tar = work / member; tar.write_bytes(subprocess.check_output(['ar', 'p', str(archive), member]))
        run('tar', '-xf', tar, '-C', sysroot); tar.unlink()
    lib = sysroot / 'usr/lib/aarch64-linux-gnu'; lib.mkdir(parents=True, exist_ok=True)
    for path in runtime.glob('*.so*'):
        if path.is_file():
            dest = lib / path.name; dest.unlink(missing_ok=True); dest.symlink_to(path.resolve())
    (sysroot / 'lib').symlink_to('usr/lib')
    (sysroot / 'usr/lib/ld-linux-aarch64.so.1').symlink_to('aarch64-linux-gnu/ld-linux-aarch64.so.1')
    moc = sysroot / inputs['moc']['path']
    moc_command = [str(qemu), '-L', str(ubuntu), str(moc)]
    version = subprocess.check_output(moc_command + ['-v'], stderr=subprocess.STDOUT, text=True).strip()
    if version != inputs['moc']['version']:
        raise ValueError('Wrong locked Qt moc version')
    qt = sysroot / 'usr/include/aarch64-linux-gnu/qt5'; src = source / 'src'
    includes = [src, sysroot / 'usr/include', sysroot / 'usr/include/android-19',
                sysroot / 'usr/include/libqtubuntu-media-signals', qt]
    includes += [qt / n for n in ['QtCore', 'QtGui', 'QtNetwork', 'QtConcurrent',
                                  'QtMultimedia', 'QtSensors', 'QtOpenGL']]
    include_flags = ['-I' + str(p) for p in includes]
    defines = ['-DQT_PLUGIN', '-DQT_NO_DEBUG', '-DQT_CORE_LIB', '-DQT_GUI_LIB',
               '-DQT_MULTIMEDIA_LIB', '-DQT_SENSORS_LIB']
    objects = work / 'objects'; objects.mkdir(); sources = sorted(src.glob('*.cpp'))
    for header in sorted(src.glob('*.h')):
        if 'Q_OBJECT' in header.read_text():
            generated = objects / ('moc_' + header.stem + '.cpp')
            run(*moc_command, *include_flags, *defines, header, '-o', generated)
            sources.append(generated)
    clang = ndk / 'toolchains/llvm/prebuilt/linux-x86_64/bin/clang++'
    flags = [str(clang), '--target=aarch64-linux-gnu', '--sysroot=' + str(sysroot),
             '--gcc-toolchain=' + str(sysroot / 'usr'), '-stdlib=libstdc++', '-std=c++14',
             '-O2', '-fPIC', '-fstack-protector-strong', *include_flags, *defines]
    def compile(path):
        obj = objects / (path.stem + '.o')
        result = subprocess.run(flags + ['-c', str(path), '-o', str(obj)],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return obj, result
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        results = list(pool.map(compile, sources))
    with (work / 'compile.log').open('wb') as log:
        for obj, result in results: log.write(result.stdout)
    if any(result.returncode for obj, result in results):
        raise ValueError('Camera compilation failed; see compile.log')
    link = ['-fuse-ld=lld', '-Wl,--no-undefined', '-Wl,-rpath-link,' + str(lib), '-L' + str(lib)]
    run(*flags, '-shared', *link, *[obj for obj, result in results],
        *['-l:' + n for n in LIBRARIES], '-o', output / 'libaalcamera.so')
    # Exercise the real worker teardown with a FIFO that deliberately has no reader.
    test = work / 'fifo-cancel'
    run(*flags, *link, base / 'fifo-cancel.cpp', src / 'audiocapture.cpp',
        objects / 'moc_audiocapture.cpp', '-l:libQt5Core.so.5', '-l:libpulse-simple.so.0',
        '-l:libpulse.so.0', '-pthread', '-o', test)
    with (output / 'fifo-cancel.log').open('w') as log:
        subprocess.run([str(qemu), '-L', str(ubuntu), str(test)], check=True,
                       stdout=log, stderr=subprocess.STDOUT, timeout=5)
    licences = output / 'licences'; licences.mkdir(); shutil.copy2(source / 'COPYING', licences / 'COPYING')
    report.write_text(json.dumps({'identity': identity, 'source_commit': origin['commit'],
                                 'patch_sha256': origin['patch_sha256'], 'moc_sha256': sha(moc),
                                 'fifo_cancel_test': 'passed under ARM64 QEMU',
                                 'artifacts': artifacts(output)}, indent=2) + '\n')
    print('Built locked Noble Qt camera plugin: ' + str(output))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('ndk', 'ubuntu-root', 'work', 'output', 'downloads', 'qemu-aarch64'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--source-cache', type=Path)
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    if args.jobs < 1: parser.error('Positive job count required')
    build(args.ndk.resolve(), args.ubuntu_root.resolve(), args.work.resolve(), args.output.resolve(),
          args.downloads.resolve(), args.qemu_aarch64.resolve(), args.source_cache, args.jobs)


if __name__ == '__main__': main()
