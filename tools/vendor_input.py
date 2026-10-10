"""Identify locked vendor or explicitly pinned local source-vendor qualification input."""
import json
import re
from pathlib import PurePosixPath
from build_manifest import sha
from build_vendor import projects


def identify_vendor(image, sources, repository, report=None, report_sha256=None):
    if image.is_symlink() or not image.is_file() or not image.stat().st_size:
        raise ValueError('Vendor must be a nonempty regular file')
    digest = sha(image)
    if report is None and report_sha256 is None:
        if digest != sources['vendor']['sha256']:
            raise ValueError('Unqualified vendor input hash')
        return {'kind': 'locked', 'sha256': digest}
    if report is None or not re.fullmatch('[0-9a-f]{64}', report_sha256 or ''):
        raise ValueError('Source vendor requires report and explicit report SHA256')
    if report.is_symlink() or not report.is_file() or sha(report) != report_sha256:
        raise ValueError('Source-vendor report checksum mismatch')
    record = json.loads(report.read_text())
    files = sources['vendor_recipe']['files']
    if (record.get('vendor_sha256') != digest
            or record.get('recipe', {}).get('manifest_sha256') != files['device/vendor/manifest.xml']
            or record.get('container_recipe_sha256') != files['device/vendor/Dockerfile']
            or record.get('builder_sha256') != files['tools/build_vendor.py']):
        raise ValueError('Source-vendor image or recipe mismatch')
    expected = projects(repository/'device/vendor/manifest.xml')
    commits = record.get('commits', {})
    patches = record.get('patches', {})
    if (set(commits) != set(expected) or len(patches) != 17
            or any(not re.fullmatch('[0-9a-f]{40}', value) for value in commits.values())
            or any(not re.fullmatch('[0-9a-f]{64}', value) for value in patches.values())
            or not re.fullmatch('sha256:[0-9a-f]{64}', record.get('container_image', ''))):
        raise ValueError('Incomplete source-vendor build provenance')
    targets = set()
    for name in patches:
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or path.parts[0] != 'patches':
            raise ValueError('Unsafe vendor patch path')
        target = str(path.parent.relative_to('patches'))
        if target not in expected:
            raise ValueError('Patch target outside vendor manifest')
        targets.add(target)
    if any(commits[path] != commit for path, commit in expected.items() if path not in targets):
        raise ValueError('Unpatched vendor commit differs from manifest')
    # The reviewed report pins patched commits; base commits remain in the manifest.
    # These checks identify inputs, and do not attest hardware or redistribution approval.
    return {'kind': 'local-source-candidate', 'sha256': digest,
            'build_report_sha256': report_sha256,
            'container_image': record['container_image'],
            'qualification': 'pending; no redistribution approval'}
