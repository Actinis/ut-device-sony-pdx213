#!/usr/bin/env python3
"""Build the pinned Noble radio plugin with restored screen-off filtering."""
import argparse
import concurrent.futures
import json
from pathlib import Path
import shutil
import subprocess
import urllib.request
from build_repowerd import run, sha

ROOT = Path(__file__).resolve().parents[1]


def build(ndk, ubuntu, work, output, downloads, source_cache=None, jobs=4):
    from sources_lock import validate, validate_ofono_inputs
    lock_path = ROOT / 'sources.lock.json'
    validate(json.loads(lock_path.read_text()), ROOT)
    base = ROOT / 'device/ofono'
    inputs = validate_ofono_inputs(json.loads((base / 'inputs.json').read_text()), base)
    runtime = ubuntu / 'usr/lib/aarch64-linux-gnu'
    for name, checksum in inputs['runtime_libraries'].items():
        if not (runtime / name).is_file() or sha(runtime / name) != checksum:
            raise ValueError('oFono locked runtime mismatch: ' + name)
    plugins = list(runtime.glob('ofono*/plugins/binderplugin.so'))
    if len(plugins) != 1 or sha(plugins[0]) != inputs['original_plugin_sha256']:
        raise ValueError('oFono distribution plugin mismatch')
    identity = {'inputs_sha256': sha(base / 'inputs.json'), 'lock_sha256': sha(lock_path),
                'builder_sha256': sha(Path(__file__)), 'runtime_libraries': inputs['runtime_libraries'],
                'ndk_properties_sha256': sha(ndk / 'source.properties')}
    if work.is_symlink() or output.is_symlink():
        raise ValueError('Linked oFono directories rejected')
    report = output / 'ofono-build-report.json'
    if report.is_file():
        saved = json.loads(report.read_text())
        if saved.get('identity') != identity or saved.get('artifacts') != artifact_hashes(output):
            raise ValueError('oFono resume identity/artifact mismatch')
        return
    if work.exists() or output.exists():
        raise ValueError('Fresh oFono work/output directories required')
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
        raise ValueError('Wrong oFono revision')
    for patch in (inputs['packaging']['patch'], inputs['patch']['file']):
        run('git', '-C', source, 'apply', '--check', base / patch)
        run('git', '-C', source, 'apply', base / patch)
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
                raise ValueError('oFono package download hash mismatch')
            partial.replace(archive)
        if sha(archive) != package['sha256']:
            raise ValueError('oFono cached package hash mismatch')
        members = subprocess.check_output(['ar', 't', str(archive)], text=True).splitlines()
        member = next(name for name in members if name.startswith('data.tar.'))
        tar = work / member
        tar.write_bytes(subprocess.check_output(['ar', 'p', str(archive), member]))
        run('tar', '-xf', tar, '-C', sysroot)
        tar.unlink()
    lib = sysroot / 'usr/lib/aarch64-linux-gnu'
    # Include transitive link dependencies from the same locked Noble rootfs.
    for path in runtime.glob('*.so*'):
        if path.is_file():
            target = lib / path.name
            target.unlink(missing_ok=True)
            target.symlink_to(path.resolve())
    (sysroot / 'lib').symlink_to('usr/lib')
    (sysroot / 'usr/lib/ld-linux-aarch64.so.1').symlink_to('aarch64-linux-gnu/ld-linux-aarch64.so.1')
    toolbin = ndk / 'toolchains/llvm/prebuilt/linux-x86_64/bin'
    cc = toolbin / 'clang'
    flags = ['--target=aarch64-linux-gnu', '--sysroot=' + str(sysroot), '-fPIC', '-fvisibility=hidden', '-O2',
             '-DGLIB_VERSION_MAX_ALLOWED=GLIB_VERSION_2_32', '-DGLIB_VERSION_MIN_REQUIRED=GLIB_VERSION_MAX_ALLOWED']
    includes = ['usr/include', 'usr/include/ofono-sailfish', 'usr/include/libmce-glib',
                'usr/include/gbinder-radio', 'usr/include/gbinder', 'usr/include/gutil',
                'usr/include/glib-2.0', 'usr/lib/aarch64-linux-gnu/glib-2.0/include',
                'usr/include/dbus-1.0', 'usr/lib/aarch64-linux-gnu/dbus-1.0/include']
    flags += ['-I' + str(sysroot / name) for name in includes] + ['-I' + str(source / 'lib/include')]
    objects = work / 'objects'
    objects.mkdir()
    files = sorted((source / 'src').glob('*.c'))
    if not files:
        raise ValueError('Missing plugin source')
    def compile_file(path):
        result = subprocess.run([str(cc), *flags, '-c', str(path), '-o', str(objects / (path.stem + '.o'))],
                                capture_output=True, text=True)
        return path.name, result.returncode, result.stdout + result.stderr
    with concurrent.futures.ThreadPoolExecutor(jobs) as pool:
        results = list(pool.map(compile_file, files))
    (output / 'compile.log').write_text('\n'.join(name + '\n' + log for name, _, log in results))
    if any(code for _, code, _ in results):
        raise ValueError('oFono compilation failed; see compile.log')
    binary = output / 'binderplugin.so'
    with (output / 'link.log').open('w') as log:
        run(cc, '--target=aarch64-linux-gnu', '--sysroot=' + str(sysroot), '--gcc-toolchain=' + str(sysroot / 'usr'), '-fuse-ld=lld', '-shared',
            '-Wl,-rpath-link,' + str(lib), '-o', binary,
            *sorted(objects.glob('*.o')), *(lib / name for name in inputs['runtime_libraries']),
            stdout=log, stderr=subprocess.STDOUT)
    run(toolbin / 'llvm-strip', '--strip-unneeded', binary)
    header = binary.read_bytes()[:20]
    if header[:5] != b'\x7fELF\x02' or header[18:20] != b'\xb7\x00':
        raise ValueError('Missing ARM64 plugin output')
    licences = output / 'licences'
    licences.mkdir()
    for path in sorted([*source.glob('COPYING*'), *source.glob('LICENSE*')]):
        shutil.copy2(path, licences / path.name)
    if not list(licences.iterdir()):
        raise ValueError('Missing upstream licences')
    report.write_text(json.dumps({'identity': identity, 'source': origin, 'packaging': inputs['packaging'],
                                 'patch': inputs['patch'], 'artifacts': artifact_hashes(output)}, indent=2) + '\n')
    print('Built locked ARM64 oFono radio plugin: ' + str(binary))


def artifact_hashes(output):
    files = [output / 'binderplugin.so', *sorted((output / 'licences').glob('*'))]
    if not files[0].is_file() or len(files) < 2 or any(p.is_symlink() or not p.is_file() for p in files):
        raise ValueError('Incomplete or linked oFono artifacts')
    return {p.relative_to(output).as_posix(): sha(p) for p in files}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('ndk', 'ubuntu-root', 'work', 'output', 'downloads'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--source-cache', type=Path)
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error('Positive job count required')
    build(args.ndk.resolve(), args.ubuntu_root.resolve(), args.work, args.output,
          args.downloads.resolve(), args.source_cache, args.jobs)


if __name__ == '__main__':
    main()
