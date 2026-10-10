#!/usr/bin/env python3
"""Build an unqualified AOSP vendor candidate; never flash, update pins or publish."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / 'device/vendor'


def execute(*args, **kwargs):
    return subprocess.run([str(a) for a in args], check=True, **kwargs)


def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def projects(manifest):
    tree = ET.parse(manifest).getroot()
    remotes = {node.get('name'): node.get('fetch', '') for node in tree.findall('remote')}
    default = tree.find('default')
    default_remote = default.get('remote') if default is not None else None
    if not remotes or any(not url.startswith('https://') for url in remotes.values()):
        raise ValueError('Vendor remotes must use HTTPS')
    result = {}
    for project in tree.findall('project'):
        path = project.get('path', project.get('name'))
        revision = project.get('revision', '')
        if project.get('remote', default_remote) not in remotes:
            raise ValueError('Unknown vendor remote')
        import re
        if (not path or Path(path).is_absolute() or '..' in Path(path).parts
                or path in result or not re.fullmatch('[0-9a-f]{40}', revision)):
            raise ValueError('Unsafe, duplicate or unpinned vendor project')
        result[path] = revision
    if result.get('rpm') != 'f683f1fb0ab85e4e2247ef6ed4910440205b1e98':
        raise ValueError('Missing pinned Android patch repository')
    return result


def prepare(source, output):
    expected = projects(RECIPE/'manifest.xml')
    identity = {'manifest_sha256': digest(RECIPE/'manifest.xml')}
    stamp = output/'prepared.json'
    if stamp.exists():
        old = json.loads(stamp.read_text())
        if old['recipe'].get('manifest_sha256') != identity['manifest_sha256'] or set(old['commits']) != set(expected):
            raise ValueError('Prepared source recipe mismatch')
        for path, commit in old['commits'].items():
            if git(source/path, 'rev-parse', 'HEAD') != commit or git(source/path, 'status', '--porcelain', '--untracked-files=all'):
                raise ValueError('Prepared vendor source changed: '+path)
        return old
    for path, commit in expected.items():
        if git(source/path, 'rev-parse', 'HEAD') != commit or git(source/path, 'status', '--porcelain', '--untracked-files=all'):
            raise ValueError('Vendor source must match the clean manifest before patching: '+path)
    patches = sorted((source/'rpm/patches').rglob('*.patch'))
    if len(patches) != 17:
        raise ValueError('Unexpected Android patch inventory')
    # Check the entire ordered series in disposable Git worktrees before touching sources.
    groups = {}
    for patch in patches:
        relative = patch.relative_to(source/'rpm/patches')
        if str(relative.parent) not in expected:
            raise ValueError('Patch target is outside manifest')
        groups.setdefault(str(relative.parent), []).append(patch)
    for path, series in groups.items():
        temporary = output/'patch-check'/path
        temporary.parent.mkdir(parents=True, exist_ok=True)
        execute('git', '-C', source/path, 'worktree', 'add', '--detach', temporary, expected[path])
        try:
            execute('git', '-C', temporary, '-c', 'user.name=UT vendor build', '-c', 'user.email=build@localhost', 'am', '--committer-date-is-author-date', *series)
        finally:
            execute('git', '-C', source/path, 'worktree', 'remove', '--force', temporary)
    for path, series in groups.items():
        execute('git', '-C', source/path, '-c', 'user.name=UT vendor build', '-c', 'user.email=build@localhost', 'am', '--committer-date-is-author-date', *series)
    record = {'recipe': identity, 'commits': {p: git(source/p, 'rev-parse', 'HEAD') for p in expected},
              'patches': {str(p.relative_to(source/'rpm')): digest(p) for p in patches}}
    stamp.write_text(json.dumps(record, indent=2)+'\n')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--android-source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--sync', action='store_true')
    parser.add_argument('--repo-launcher', type=Path)
    parser.add_argument('--container-engine', type=Path)
    parser.add_argument('--container-image')
    parser.add_argument('--jobs', type=int, default=8)
    args = parser.parse_args()
    source, output = args.android_source.resolve(), args.output.resolve()
    if source == output or source in output.parents or output in source.parents or args.jobs < 1:
        parser.error('Separate source/output directories and positive jobs required')
    output.mkdir(parents=True, exist_ok=True)
    from sources_lock import validate
    lock = validate(json.loads((ROOT/'sources.lock.json').read_text()), ROOT)['sources']
    if args.sync:
        if not args.repo_launcher:
            parser.error('--sync requires an explicit repo launcher')
        manifest = output/'manifest'
        if not manifest.exists():
            manifest.mkdir()
            (manifest/'default.xml').write_bytes((RECIPE/'manifest.xml').read_bytes())
            execute('git', 'init', manifest)
            execute('git', '-C', manifest, 'add', 'default.xml')
            execute('git', '-C', manifest, '-c', 'user.name=UT vendor build', '-c', 'user.email=build@localhost', 'commit', '-m', 'Pinned vendor manifest')
        if (manifest/'default.xml').read_bytes() != (RECIPE/'manifest.xml').read_bytes():
            raise ValueError('Sync manifest differs from locked recipe')
        source.mkdir(parents=True, exist_ok=True)
        execute(args.repo_launcher.resolve(), 'init', '-u', manifest, '--depth=1', '--no-clone-bundle',
                '--repo-url='+lock['repo_tool']['url'], '--repo-rev='+lock['repo_tool']['commit'], cwd=source)
        execute(args.repo_launcher.resolve(), 'sync', '-c', '--no-tags', '--no-clone-bundle', '-j'+str(args.jobs), cwd=source)
    if git(source/'.repo/repo', 'rev-parse', 'HEAD') != lock['repo_tool']['commit']:
        raise ValueError('Repo implementation differs from lock')
    record = prepare(source, output)
    (output/'home').mkdir(exist_ok=True)
    if args.prepare_only:
        return
    if not args.container_engine or not args.container_image:
        parser.error('Explicit container engine and immutable image ID required')
    import re
    if not re.fullmatch(r'sha256:[0-9a-f]{64}', args.container_image):
        parser.error('Use the locally built Docker image ID, not a mutable tag')
    # Compilation and package list run as the caller; never mount Docker socket or OEM.
    command = ('set -e; dpkg-query -W > /output/host-packages.txt; '
               'source build/envsetup.sh; lunch aosp_xqbt52-user; '
               f'make -j{args.jobs} vendorimage simg2img; '
               'cp "$OUT/vendor.img" /output/vendor.sparse.img; '
               '"$OUT_DIR/host/linux-x86/bin/simg2img" /output/vendor.sparse.img /output/vendor.img')
    execute(args.container_engine, 'run', '--rm', '--network=none', '--user', f'{os.getuid()}:{os.getgid()}',
            '--env', 'BUILD_USERNAME=utbuilder', '--env', 'BUILD_HOSTNAME=vendor-builder',
            '--env', 'OUT_DIR=/output/android-out', '--env', 'GOCACHE=/output/go-cache',
            '--mount', f'type=bind,src={source},dst=/work',
            '--mount', f'type=bind,src={output},dst=/output',
            args.container_image, '/bin/bash', '-c', command)
    record.update({'status': 'built; hardware and redistribution qualification pending',
                   'container_image': args.container_image,
                   'container_recipe_sha256': digest(RECIPE/'Dockerfile'),
                   'builder_sha256': digest(Path(__file__)),
                   'vendor_sha256': digest(output/'vendor.img'),
                   'host_packages_sha256': digest(output/'host-packages.txt')})
    (output/'vendor-build-report.json').write_text(json.dumps(record, indent=2)+'\n')


if __name__ == '__main__':
    main()
