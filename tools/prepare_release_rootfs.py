#!/usr/bin/env python3
"""Apply reproducible public integration to an extracted official UT rootfs."""
import argparse, os, shutil, subprocess
from pathlib import Path

def install_ofono(root, output):
    import json
    from build_ofono import ROOT, artifact_hashes, sha
    from sources_lock import validate_ofono_inputs
    base=ROOT/'device/ofono'
    inputs=validate_ofono_inputs(json.loads((base/'inputs.json').read_text()),base)
    report=json.loads((output/'ofono-build-report.json').read_text())
    identity=report.get('identity',{})
    if identity.get('inputs_sha256')!=sha(base/'inputs.json') or identity.get('lock_sha256')!=sha(ROOT/'sources.lock.json') or identity.get('builder_sha256')!=sha(ROOT/'tools/build_ofono.py') or report.get('artifacts')!=artifact_hashes(output):
        raise ValueError('oFono packaging identity/artifact mismatch')
    candidates=list((root/'usr/lib/aarch64-linux-gnu').glob('ofono*/plugins/binderplugin.so'))
    if len(candidates)!=1 or candidates[0].is_symlink() or sha(candidates[0])!=inputs['original_plugin_sha256']:
        raise ValueError('Wrong distribution oFono plugin baseline')
    dest=candidates[0]
    shutil.copy2(output/'binderplugin.so',dest);os.chown(dest,0,0);dest.chmod(0o644)
    licences=root/'usr/share/doc/utxperia-ofono'
    licences.mkdir(parents=True,exist_ok=True)
    for src in (output/'licences').iterdir():
        dest=licences/src.name;shutil.copy2(src,dest);os.chown(dest,0,0)


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True)
    p.add_argument('--artifacts',type=Path,required=True);a=p.parse_args()
    root=a.root.resolve();workspace=Path(__file__).resolve().parents[1]
    if root==Path('/') or not (root/'usr/sbin/nfcd').exists():raise SystemExit('Wrong Ubuntu rootfs')
    overlay=workspace/'overlay'
    for src in overlay.rglob('*'):
        if '__pycache__' in src.parts:continue
        dest=root/src.relative_to(overlay)
        if src.is_dir():dest.mkdir(parents=True,exist_ok=True)
        elif src.is_symlink():
            dest.unlink(missing_ok=True);dest.symlink_to(os.readlink(src))
        else:dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
        os.chown(dest,0,0,follow_symlinks=False)
    for source,target in [('out/libvndservicemanager-apparmor-compat.so','usr/local/lib/utxperia/libvndservicemanager-apparmor-compat.so'),('out/utxperia-reboot-bootloader','usr/bin/utxperia-reboot-bootloader')]:
        dest=root/target;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a.artifacts/source,dest);os.chown(dest,0,0)
    for name in ('libubuntu_application_api.so', 'libubuntu_application_old.so', 'libutxperia-gnss-assistance.so'):
        dest=root/'usr/local/lib/utxperia/gnss'/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(a.artifacts/'out/gnss'/name,dest);os.chown(dest,0,0)
    dest=root/'usr/local/libexec/utxperia-repowerd'
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(a.artifacts/'out/repowerd/repowerd',dest);os.chown(dest,0,0);dest.chmod(0o755)
    install_ofono(root,a.artifacts/'out/ofono')
    from build_nfc import ARTIFACTS
    nfc=root/'usr/local/lib/utxperia/nfc'
    nfc.mkdir(parents=True,exist_ok=True)
    for name in ARTIFACTS:
        dest=nfc/name;shutil.copy2(a.artifacts/'out/nfc'/name,dest);os.chown(dest,0,0)
    plugins=nfc/'plugins';plugins.mkdir(exist_ok=True)
    if not (root/'usr/lib/nfcd/plugins/binder.so').exists():raise SystemExit('Missing distribution NFC binder plugin')
    for src in (root/'usr/lib/nfcd/plugins').iterdir():
        dest=plugins/src.name;dest.unlink(missing_ok=True)
        dest.symlink_to('/usr/local/lib/utxperia/nfc/binder.so' if src.name=='binder.so' else '/usr/lib/nfcd/plugins/'+src.name)
        os.chown(dest,0,0,follow_symlinks=False)
    # Add only documented groups; never copy the test device's passwd/shadow.
    file=root/'etc/group';lines=[]
    additions={'android_graphics':['lightdm'],'video':['lightdm'],'render':['lightdm','phablet'],'android_input':['lightdm']}
    for line in file.read_text().splitlines():
        fields=line.split(':')
        if fields[0] in additions:
            members=[v for v in fields[3].split(',') if v]
            fields[3]=','.join(dict.fromkeys(members+additions[fields[0]]))
        lines.append(':'.join(fields))
    file.write_text('\n'.join(lines)+'\n')
    for name in ['utxperia-wlan.service','utxperia-usb.service','utxperia-usb-internet.service','utxperia-usb-mtp.timer','utxperia-firstboot.service','utxperia-tilt.service']:
        subprocess.run(['systemctl','--root',str(root),'enable',name],check=True)
    subprocess.run(['systemctl','--root',str(root),'disable','ssh.service','ssh.socket','utxperia-usb-mtp.service'],check=True)
    # The port owns its configfs gadget; stock usb-moded must not compete.
    for name in ['etc/systemd/system/usb-moded.service',
                 'etc/systemd/user/mtp-server-usb-moded-watcher.service']:
        dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True)
        dest.unlink(missing_ok=True);dest.symlink_to('/dev/null')
    # A pristine rootfs has no syslog/auth.log until logging creates them.
    logrotate=root/'etc/logrotate.d/touch-syslog'
    text=logrotate.read_text()
    if 'missingok' not in text:
        logrotate.write_text(text.replace(' {\n', ' {\n    missingok\n'))
    for directory,name,target in [
        ('etc/systemd/user/default.target.wants','audiosystem-passthrough-qti.service','/usr/lib/systemd/user/audiosystem-passthrough-qti.service'),
        ('etc/systemd/user/pulseaudio.service.wants','utxperia-call-audio.service','/usr/lib/systemd/user/utxperia-call-audio.service')]:
        dest=root/directory/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.unlink(missing_ok=True);dest.symlink_to(target)
    for name in ['root/.ssh','home/phablet/.ssh','etc/NetworkManager/system-connections','var/lib/NetworkManager','var/lib/ofono','var/lib/bluetooth','var/log/journal']:
        path=root/name
        if path.is_dir():shutil.rmtree(path)
    for path in (root/'etc/ssh').glob('ssh_host_*'):path.unlink()
    for name in ['etc/machine-id','var/lib/dbus/machine-id']:
        path=root/name;path.unlink(missing_ok=True)
    (root/'etc/machine-id').write_text('')
    for name in ['root','home/phablet','var/log','tmp']:
        path=root/name
        for f in path.glob('.*history'):f.unlink()
    # No provisioning identity or wizard-completed marker is shipped.
    if (root/'home/phablet/.config/lomiri/wizard-has-run').exists():raise SystemExit('Unexpected wizard-completed state')
    print('Clean rootfs integration prepared; SSH disabled, fresh wizard and per-device identity')
if __name__=='__main__':main()
