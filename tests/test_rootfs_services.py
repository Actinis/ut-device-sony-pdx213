import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from prepare_release_rootfs import configure_services

@unittest.skipUnless(shutil.which('systemctl'), 'systemd tools required')
class RootfsServiceTests(unittest.TestCase):
    def test_user_image_removes_development_gateway_and_keeps_local_usb(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);units=root/'etc/systemd/system';units.mkdir(parents=True)
            names=['utxperia-wlan.service','utxperia-usb.service','utxperia-usb-mtp.timer',
                'utxperia-firstboot.service','utxperia-tilt.service','ssh.service','ssh.socket',
                'utxperia-usb-mtp.service','utxperia-usb-internet.service']
            for name in names:
                (units/name).write_text('[Unit]\nDescription=Test fixture\n[Install]\nWantedBy=multi-user.target\n')
            subprocess.run(['systemctl','--root',d,'enable','utxperia-usb-internet.service'],check=True,capture_output=True)
            configure_services(root)
            wants=units/'multi-user.target.wants'
            self.assertFalse((wants/'utxperia-usb-internet.service').is_symlink())
            self.assertFalse((wants/'ssh.service').is_symlink())
            self.assertTrue((wants/'utxperia-usb.service').is_symlink())
            self.assertTrue((wants/'utxperia-wlan.service').is_symlink())
            self.assertTrue((units/'utxperia-usb-internet.service').is_file())

if __name__=='__main__':unittest.main()
