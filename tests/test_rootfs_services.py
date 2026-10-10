import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from prepare_release_rootfs import configure_services, prepare_radio_state

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

    def test_mtp_does_not_start_a_development_gateway(self):
        root=Path(__file__).resolve().parents[1]
        unit=(root/'overlay/etc/systemd/system/utxperia-usb-mtp.service').read_text()
        self.assertNotIn('utxperia-usb-internet.service',unit)
        self.assertIn('mtp-server.service',unit)

class RadioStateTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('fakeroot'), 'fakeroot required for ownership check')
    def test_clean_image_keeps_empty_radio_owned_storage(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'etc').mkdir()
            (root/'etc/passwd').write_text('radio:x:1001:1001:radio:/nonexistent:/bin/false\n')
            state=root/'var/lib/ofono';state.mkdir(parents=True)
            (state/'private-subscriber-settings').write_text('must not ship')
            tools=Path(__file__).resolve().parents[1]/'tools'
            script="import sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from prepare_release_rootfs import prepare_radio_state;r=Path(sys.argv[2]);prepare_radio_state(r);p=r/'var/lib/ofono';assert not list(p.iterdir());assert p.stat().st_uid==1001 and p.stat().st_gid==1001;assert p.stat().st_mode & 0o777 == 0o700"
            subprocess.run(['fakeroot',sys.executable,'-c',script,str(tools),str(root)],check=True)

    def test_linked_radio_state_is_rejected_without_touching_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'etc').mkdir()
            (root/'etc/passwd').write_text('radio:x:1001:1001:radio:/nonexistent:/bin/false\n')
            target=root/'preserved';target.mkdir();(target/'private').write_text('preserve')
            state=root/'var/lib/ofono';state.parent.mkdir(parents=True);state.symlink_to(target)
            with self.assertRaises(ValueError):prepare_radio_state(root)
            self.assertEqual((target/'private').read_text(),'preserve')

if __name__=='__main__':unittest.main()
