#!/usr/bin/env python3
"""Generate release metadata for reviewed image files; never flash or publish."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def package(images, output, lock, device_commit, tag, build_url):
    if not re.fullmatch(r"pdx213-noble-port-v[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.]+)?", tag):
        raise ValueError("Invalid device release tag")
    if not re.fullmatch(r"[0-9a-f]{40}", device_commit):
        raise ValueError("Full device commit required")
    if not re.fullmatch(r"https://github.com/Actinis/ut-device-sony-pdx213/actions/runs/[0-9]+", build_url):
        raise ValueError("Exact device repository build run URL required")
    data = json.loads(lock.read_text())
    if data.get("status") != "locked" or data.get("ubuntu_touch") != "24.04" or data.get("device") != "sony-pdx213":
        raise ValueError("A locked Sony Ubuntu Touch 24.04 source manifest is required")
    sources = data.get("sources", {})
    if set(sources) != {"kernel", "rootfs", "halium_gsi", "toolchain"}:
        raise ValueError("Complete source pins required")
    if not re.fullmatch(r"[0-9a-f]{40}", sources["kernel"].get("commit", "")):
        raise ValueError("Full kernel commit required")
    for name, source in sources.items():
        if not isinstance(source.get("url"), str) or not source["url"].startswith("https://"):
            raise ValueError("HTTPS source URL required")
        if name != "kernel" and (not source.get("version") or not re.fullmatch(r"[0-9a-f]{64}", source.get("sha256", ""))):
            raise ValueError("Version and source checksum required")
    artifacts = []
    for path in sorted(images.iterdir()):
        if path.is_symlink() or not path.is_file() or not re.fullmatch(re.escape(tag) + r"-[a-z0-9-]+\.img", path.name):
            raise ValueError("Input must contain only regular, release-named image files")
        if path.stat().st_size == 0:
            raise ValueError("Empty images are forbidden")
        digest = hashlib.sha256()
        with path.open('rb') as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b''):
                digest.update(chunk)
        artifacts.append({"name": path.name, "bytes": path.stat().st_size, "sha256": digest.hexdigest()})
    if not artifacts:
        raise ValueError("No images supplied")
    if output.exists():
        raise ValueError("Output directory must not already exist")
    output.mkdir(parents=True)
    manifest = {"schema_version": 1, "tag": tag, "device": data["device"], "ubuntu_touch": "24.04", "device_commit": device_commit, "kernel_commit": sources["kernel"]["commit"], "build_url": build_url, "qualification": "pending", "artifacts": artifacts}
    (output / 'release-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (output / 'sources.lock.json').write_text(json.dumps(data, indent=2) + '\n')
    hashes = [(a['name'], a['sha256']) for a in artifacts]
    hashes += [(p.name, hashlib.sha256(p.read_bytes()).hexdigest()) for p in [output/'release-manifest.json', output/'sources.lock.json']]
    (output / 'SHA256SUMS').write_text(''.join(f'{digest}  {name}\n' for name, digest in hashes))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['images', 'output', 'lock']:
        parser.add_argument('--' + name, required=True, type=Path)
    for name in ['device-commit', 'tag', 'build-url']:
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    try:
        package(args.images, args.output, args.lock, args.device_commit, args.tag, args.build_url)
    except (ValueError, KeyError, TypeError) as error:
        parser.exit(2, f'{error}\n')
