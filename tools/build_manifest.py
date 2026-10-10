"""Identity and content checks for completed Noble kernel/boot builds."""
import hashlib
import json
from pathlib import Path
import stat
import subprocess

REQUIRED_ARTIFACTS = {
    'Image.gz-dtb', 'dtbo.img', 'boot.img', 'boot.initrd.gz', 'boot.json',
    'utxperia-reboot-bootloader', 'libvndservicemanager-apparmor-compat.so',
    'gnss/libubuntu_application_api.so', 'gnss/libubuntu_application_old.so',
    'gnss/libutxperia-gnss-assistance.so',
    'ofono/binderplugin.so', 'ofono/ofono-build-report.json', 'ofono/licences/LICENSE',
    'repowerd/repowerd', 'repowerd/repowerd-build-report.json',
    'nfc/nfcd', 'nfc/binder.so', 'nfc/libncicore.so.1',
    'nfc/libnciplugin.so.1', 'nfc/nfc_nci_nxp.so',
    'nfc/vendor.nxp.nxpese@1.0.so', 'nfc/nfc-build-report.json',
}


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def build_identity(repository, build_id, sources):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(repository), *args], text=True).strip()
    if git('status', '--porcelain', '--untracked-files=no'):
        raise ValueError('Device checkout has tracked changes')
    if git('status', '--porcelain', '--untracked-files=all', '--',
           'tools', 'device', 'overlay', 'sources.lock.json'):
        raise ValueError('Device build inputs have uncommitted changes')
    return {
        'schema_version': 2,
        'build_id': build_id,
        'device_commit': git('rev-parse', 'HEAD'),
        'lock_sha256': sha(repository / 'sources.lock.json'),
        'sources': sources,
    }


def inventory(out):
    if out.is_symlink() or not out.is_dir():
        raise ValueError('Build out must be a real directory, not a link')
    files = {}
    for path in sorted(out.rglob('*')):
        if path.is_symlink():
            raise ValueError('Linked build artifact: ' + str(path.relative_to(out)))
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError('Non-regular build artifact: ' + str(path))
        name = path.relative_to(out).as_posix()
        if name != 'build-report.json':
            files[name] = {'sha256': sha(path), 'mode': stat.S_IMODE(path.stat().st_mode)}
    return files


def check_artifacts(out, report):
    release = report.get('kernel_release')
    if not isinstance(release, str) or not release or Path(release).name != release or release in ('.', '..'):
        raise ValueError('Missing or invalid kernel release')
    prefix = 'modules/lib/modules/' + release + '/'
    expected = report.get('artifacts')
    if not isinstance(expected, dict) or not REQUIRED_ARTIFACTS <= expected.keys():
        raise ValueError('Missing required kernel/boot/helper artifacts')
    if not {prefix + name for name in ('modules.dep', 'modules.order', 'modules.builtin')} <= expected.keys():
        raise ValueError('Missing required kernel module metadata')
    modules = [name for name in expected if name.startswith(prefix) and name.endswith('.ko')]
    if not modules or any(name.startswith('modules/') and not name.startswith(prefix) for name in expected):
        raise ValueError('Missing modules or mixed kernel releases')
    if expected != inventory(out):
        raise ValueError('Artifact inventory, hashes or modes differ from build report')
    if not expected['utxperia-reboot-bootloader']['mode'] & 0o111:
        raise ValueError('Reboot helper is not executable')
    return out / 'modules/lib/modules'


def verify_build(build, expected_identity):
    if build.is_symlink():
        raise ValueError('Linked build directory is not an independent build')
    identity = json.loads((build / 'input-identity.json').read_text())
    report = json.loads((build / 'out/build-report.json').read_text())
    if identity != expected_identity:
        raise ValueError('Build input identity differs from current checkout/lock/build ID')
    if any(report.get(key) != value for key, value in expected_identity.items()):
        raise ValueError('Completed build report differs from current checkout/lock/build ID')
    return check_artifacts(build / 'out', report)


def write_report(build, identity, kernel_release):
    report = dict(identity, kernel_release=kernel_release,
                  scope='kernel, DTBO, helper, GNSS/NFC libraries, oFono, Repowerd and boot; no userdata or hardware qualification',
                  artifacts=inventory(build / 'out'))
    check_artifacts(build / 'out', report)
    temporary = build / 'build-report.tmp'
    temporary.write_text(json.dumps(report, indent=2) + '\n')
    temporary.replace(build / 'out/build-report.json')


def prepare_build(build, identity, resume=False):
    """Reject unknown/stale resume state before invalidating any prior output."""
    if build.is_symlink() or (build / 'out').is_symlink():
        raise ValueError('Linked build/output directory rejected')
    marker = build / 'input-identity.json'
    if resume and (not marker.is_file() or json.loads(marker.read_text()) != identity):
        raise ValueError('Resume requires the same device commit, lock and build ID')
    build.mkdir(parents=True, exist_ok=resume)
    (build / 'out').mkdir(exist_ok=resume)
    marker.write_text(json.dumps(identity, indent=2) + '\n')
    (build / 'out/build-report.json').unlink(missing_ok=True)
