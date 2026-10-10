#!/usr/bin/env python3
"""Assemble a full CI candidate only from a reviewed, public locked vendor input."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request

from sources_lock import validate
from build_manifest import sha
from prepare_install_bundle import flashing_instructions
ROOT = Path(__file__).resolve().parents[1]


def check_vendor(entry):
    if entry.get('kind') != 'artifact' or entry.get('redistribution_approved') is not True:
        raise ValueError('Full CI packaging requires a public checksum-pinned vendor artifact with completed redistribution review')
    return entry


def fetch(entry, directory):
    destination = directory/entry['filename']
    if not destination.exists():
        partial = destination.with_suffix(destination.suffix+'.partial')
        with urllib.request.urlopen(entry['url'], timeout=60) as source, partial.open('wb') as target:
            shutil.copyfileobj(source, target)
        if sha(partial) != entry['sha256']:
            raise ValueError('Download checksum mismatch: '+entry['filename'])
        partial.replace(destination)
    if sha(destination) != entry['sha256']:
        raise ValueError('Cached input checksum mismatch: '+entry['filename'])
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-id', required=True)
    for tool in ('mksquashfs', 'mke2fs', 'img2simg'):
        parser.add_argument('--'+tool, type=Path, required=True)
    args = parser.parse_args()
    lock = validate(json.loads((ROOT/'sources.lock.json').read_text()), ROOT)['sources']
    vendor = check_vendor(lock['vendor'])
    data = Path(os.environ['UT_PORTS_DATA_DIR']).resolve()
    downloads = data/'downloads'
    downloads.mkdir(parents=True, exist_ok=True)
    vendor_path = fetch(vendor, downloads)
    encoded = fetch(lock['avbtool'], downloads)
    raw = base64.b64decode(encoded.read_bytes(), validate=True)
    if hashlib.sha256(raw).hexdigest() != lock['avbtool']['decoded_sha256']:
        raise ValueError('Decoded AVB utility checksum mismatch')
    avbtool = data/'toolchains/avbtool.py'
    avbtool.parent.mkdir(parents=True, exist_ok=True)
    avbtool.write_bytes(raw); avbtool.chmod(0o755)
    command = ['fakeroot', 'python3', str(ROOT/'tools/package_userdata.py'), '--build-id', args.build_id,
               '--vendor', str(vendor_path), '--avbtool', str(avbtool)]
    for tool in ('mksquashfs', 'mke2fs', 'img2simg'):
        command += ['--'+tool, str(getattr(args, tool))]
    subprocess.run(command, check=True)
    build = data/'builds/pdx213'/args.build_id
    package = build/'userdata-package'
    # Preserve all image/metadata names; OEM is never bundled.
    files = {'boot.img': build/'out/boot.img', 'dtbo.img': build/'out/dtbo.img',
             'userdata.img': package/'userdata.img', 'vbmeta.img': package/'vbmeta.img',
             'assembly-report.json': package/'assembly-report.json',
             'build-report.json': build/'out/build-report.json',
             'input-identity.json': build/'input-identity.json',
             'sources.lock.json': ROOT/'sources.lock.json'}
    archive_candidate(build, package, files)


def archive_candidate(build, package, files):
    instructions = package/'FLASHING.md'
    device_commit = json.loads((build/'out/build-report.json').read_text())['device_commit']
    instructions.write_text(flashing_instructions(False, device_commit))
    files['FLASHING.md'] = instructions
    manifest = package/'candidate-manifest.json'
    manifest.write_text(json.dumps({'schema_version': 1, 'qualification': 'pending; not an installation release',
                                   'sony_oem': 'excluded; user obtains directly from Sony',
                                   'artifacts': {name: {'sha256': sha(path), 'bytes': path.stat().st_size}
                                                 for name, path in files.items()}}, indent=2)+'\n')
    files['candidate-manifest.json'] = manifest
    checksums = package/'SHA256SUMS'
    checksums.write_text(''.join(f'{sha(path)}  {name}\n' for name, path in files.items()))
    files['SHA256SUMS'] = checksums
    with tarfile.open(build/'pdx213-noble-full-candidate.tar.gz', 'w:gz', compresslevel=1) as archive:
        for name, path in files.items():
            archive.add(path, arcname=name, recursive=False)


if __name__ == '__main__':
    main()
