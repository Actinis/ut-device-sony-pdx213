#!/usr/bin/env python3
"""Publish verified kernel/boot outputs; never build, flash or bundle vendor images."""
import argparse
import base64
import json
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile

from build_manifest import sha, verify_build
from sources_lock import validate

REPOSITORY = 'Actinis/ut-device-sony-pdx213'


def gh(*args):
    return subprocess.check_output(['gh', *args], text=True)


def api(path):
    return json.loads(gh('api', path))


def check_run(run):
    if (run['repository']['full_name'] != REPOSITORY
            or run['head_repository']['full_name'] != REPOSITORY
            or run['path'] != '.github/workflows/build.yml'
            or run['status'] != 'completed' or run['conclusion'] != 'success'
            or run['event'] not in ('push', 'workflow_dispatch')):
        raise ValueError('Only successful trusted kernel/boot workflow runs can be published')
    branch = run['head_branch']
    tagged = re.fullmatch(r'pdx213-noble-port-v([0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.]+)?)', branch)
    if branch != 'main' and not tagged:
        raise ValueError('Only main or explicit port release tags can be published')
    if not re.fullmatch(r'[0-9a-f]{40}', run['head_sha']):
        raise ValueError('Exact source commit required')
    return tagged.group(1) if tagged else None


def extract(archive, destination):
    # Accept exactly the regular files/directories emitted by the build archive.
    with tarfile.open(archive) as stream:
        for member in stream.getmembers():
            name = Path(member.name)
            if (name.is_absolute() or '..' in name.parts
                    or not name.parts or name.parts[0] not in ('out', 'input-identity.json')
                    or not (member.isfile() or member.isdir())):
                raise ValueError('Unsafe or unexpected archive member')
            if name.parts[0] == 'input-identity.json' and (len(name.parts) != 1 or not member.isfile()):
                raise ValueError('Invalid identity file')
        stream.extractall(destination, filter='data')


def prepare(download, output, lock_bytes, run):
    port_version = check_run(run)
    lock = json.loads(lock_bytes)
    validate(lock)
    version = lock['sources']['rootfs']['version']
    match = re.search(r'\b(24\.04-[0-9]+\.x)\b', version)
    if not match:
        raise ValueError('The locked rootfs must name its Ubuntu Touch release series')
    series = match.group(1)
    build_id = f"ci-{run['id']}-{run['run_attempt']}"
    identity = {'schema_version': 2, 'build_id': build_id,
                'device_commit': run['head_sha'], 'lock_sha256': hashlib.sha256(lock_bytes).hexdigest(),
                'sources': lock['sources']}
    unpacked = download / 'verified-build'
    extract(download / 'pdx213-noble-kernel-boot.tar.gz', unpacked)
    verify_build(unpacked, identity)
    for name in ['input-identity.json', 'out/build-report.json']:
        if (download / name).read_bytes() != (unpacked / name).read_bytes():
            raise ValueError('Artifact metadata differs from archived metadata')
    tag = run['head_branch'] if port_version else f"pdx213-ut{series}-daily-{run['id']}-{run['run_attempt']}-{run['head_sha'][:7]}"
    output.mkdir()
    for name in ['boot.img', 'dtbo.img']:
        shutil.copyfile(unpacked / 'out' / name, output / f'{tag}-{name}')
    shutil.copyfile(download / 'pdx213-noble-kernel-boot.tar.gz', output / f'{tag}-kernel-boot.tar.gz')
    shutil.copyfile(unpacked / 'out/build-report.json', output / 'build-report.json')
    shutil.copyfile(unpacked / 'input-identity.json', output / 'input-identity.json')
    (output / 'sources.lock.json').write_bytes(lock_bytes)
    manifest = {'schema_version': 2, 'device': lock['device'], 'ubuntu_touch': '24.04',
                'ubuntu_touch_series': series, 'rootfs_version': version,
                'port_version': port_version, 'channel': 'candidate' if port_version else 'daily',
                'tag': tag, 'device_commit': run['head_sha'], 'kernel_commit': lock['sources']['kernel']['commit'],
                'build_id': build_id, 'build_url': run['html_url'], 'qualification': 'pending',
                'scope': 'experimental kernel/boot only; not a complete installation',
                'artifacts': [{'name': p.name, 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in sorted(output.iterdir())]}
    (output / 'release-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (output / 'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in sorted(output.iterdir()) if p.name != 'SHA256SUMS'))
    title = f"Xperia 10 III — UT {series} — " + (f'port {port_version}' if port_version else f"daily build {run['id']}.{run['run_attempt']}")
    notes = f'''Experimental Actinis community kernel/boot build for Sony Xperia 10 III XQ-BT52.

- Ubuntu Touch series: **{series}**; rootfs: **{version}**.
- Port version: **{port_version or 'development snapshot (identified by commit)'}**.
- Device commit: `{run['head_sha']}`.
- Kernel commit: `{lock['sources']['kernel']['commit']}`.
- [Exact build run]({run['html_url']}).

**Not a complete installable Ubuntu Touch image.** Vendor/OEM, userdata and an installer are excluded. Compatibility with an arbitrary installed system is not qualified. Hardware and installation qualification of these exact outputs remains pending. This is not an official UBports release or an OTA update channel.

The kernel/boot archive includes modules, helpers, reports and file modes. Verify downloads with `sha256sum -c SHA256SUMS`. See [build scope and installation gates](https://github.com/{REPOSITORY}/blob/{run['head_sha']}/docs/INSTALLATION-QUALIFICATION.md) before using images.
'''
    return tag, title, notes, bool(port_version)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True, type=int)
    args = parser.parse_args()
    run = api(f'repos/{REPOSITORY}/actions/runs/{args.run_id}')
    version = check_run(run)
    if version:
        ref = api(f"repos/{REPOSITORY}/git/ref/tags/{run['head_branch']}")['object']
        while ref['type'] == 'tag':
            ref = api(f"repos/{REPOSITORY}/git/tags/{ref['sha']}")['object']
        if ref['type'] != 'commit' or ref['sha'] != run['head_sha']:
            raise ValueError('Release tag no longer points to the built commit')
    artifact_name = f"pdx213-noble-kernel-boot-{run['id']}-{run['run_attempt']}"
    artifacts = api(f'repos/{REPOSITORY}/actions/runs/{args.run_id}/artifacts?per_page=100')['artifacts']
    selected = [a for a in artifacts if a['name'] == artifact_name and not a['expired']]
    if len(selected) != 1:
        raise ValueError('Exactly one current build artifact is required')
    lock_data = api(f"repos/{REPOSITORY}/contents/sources.lock.json?ref={run['head_sha']}")
    lock_bytes = base64.b64decode(lock_data['content'])
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        download = root / 'download'
        gh('run', 'download', str(args.run_id), '--repo', REPOSITORY, '--name', artifact_name, '--dir', str(download))
        output = root / 'release'
        tag, title, notes, draft_only = prepare(download, output, lock_bytes, run)
        existing = subprocess.run(['gh', 'release', 'view', tag, '--repo', REPOSITORY, '--json', 'tagName'], capture_output=True)
        if existing.returncode == 0:
            raise ValueError('Release already exists; published assets are never overwritten')
        # Create the exact ref first: Release API workflow-scope checks differ
        # when asked to create a tag implicitly on a historical workflow commit.
        tag_result = subprocess.run(['gh', 'api', f'repos/{REPOSITORY}/git/ref/tags/{tag}'], capture_output=True, text=True)
        if tag_result.returncode != 0:
            gh('api', '--method', 'POST', f'repos/{REPOSITORY}/git/refs', '-f', 'ref=refs/tags/' + tag, '-f', 'sha=' + run['head_sha'])
        ref = api(f'repos/{REPOSITORY}/git/ref/tags/{tag}')['object']
        while ref['type'] == 'tag':
            ref = api(f"repos/{REPOSITORY}/git/tags/{ref['sha']}")['object']
        if ref['type'] != 'commit' or ref['sha'] != run['head_sha']:
            raise ValueError('Existing tag differs from built commit')
        # A partial upload remains a draft. Publish only after every asset was uploaded.
        body = root / 'notes.md'; body.write_text(notes)
        gh('release', 'create', tag, '--repo', REPOSITORY, '--verify-tag', '--draft', '--prerelease', '--latest=false', '--title', title, '--notes-file', str(body), *[str(p) for p in sorted(output.iterdir())])
        if not draft_only:
            gh('release', 'edit', tag, '--repo', REPOSITORY, '--draft=false', '--prerelease', '--latest=false')
        print(f"{'Draft' if draft_only else 'Prerelease'}: https://github.com/{REPOSITORY}/releases/tag/{tag}")


if __name__ == '__main__':
    main()
