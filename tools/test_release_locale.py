#!/usr/bin/env python3
"""Exercise the shipped Debian tmpfiles migration of Ubuntu's locale file."""
import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('rootfs', type=Path)
args = parser.parse_args()
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    (root/'etc/default').mkdir(parents=True)
    (root/'etc/tmpfiles.d').mkdir()
    shutil.copy2(args.rootfs/'usr/lib/tmpfiles.d/debian.conf', root/'etc/tmpfiles.d/debian.conf')
    (root/'etc/default/locale').write_text('LANG=en_US.UTF-8\n')
    (root/'etc/locale.conf').write_text('#LANG=C.UTF-8\n')
    subprocess.run(['systemd-tmpfiles', '--root='+str(root), '--create', '--prefix=/etc/default/locale'], check=True)
    assert (root/'etc/default/locale').is_symlink()
    assert not any(line.startswith('LANG=') for line in (root/'etc/default/locale').read_text().splitlines())
    shutil.copy2(args.rootfs/'etc/locale.conf', root/'etc/locale.conf')
    subprocess.run(['systemd-tmpfiles', '--root='+str(root), '--create', '--prefix=/etc/default/locale'], check=True)
    assert (root/'etc/default/locale').read_text() == 'LANG=en_US.UTF-8\n'
print('Real Debian tmpfiles rule reproduces the old missing locale; corrected canonical locale survives migration')
