import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = SourceFileLoader('biometry_startup', str(ROOT/'overlay/usr/local/sbin/utxperia-biometryd'))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)


class BiometryStartup(unittest.TestCase):
    def test_hal_initialization_retries_then_succeeds(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory)/'attempts'
            code = "from pathlib import Path; p=Path(__import__('sys').argv[1]); n=int(p.read_text()) if p.exists() else 0; p.write_text(str(n+1)); raise SystemExit(78 if n<2 else 0)"
            self.assertEqual(module.run([sys.executable, '-c', code, str(state)], timeout=3, interval=0.01), 0)
            self.assertEqual(state.read_text(), '3')

    def test_other_failure_is_not_hidden(self):
        self.assertEqual(module.run([sys.executable, '-c', 'raise SystemExit(1)'], interval=0), 1)

    def test_unavailable_hal_is_bounded(self):
        self.assertEqual(module.run([sys.executable, '-c', 'raise SystemExit(78)'], timeout=0, interval=0), 78)

    def test_optional_ui_order_and_real_dbus_readiness(self):
        unit = (ROOT/'overlay/etc/systemd/system/biometryd.service.d/utxperia-startup.conf').read_text()
        ui = (ROOT/'overlay/etc/systemd/system/lightdm.service.d/utxperia-biometry.conf').read_text()
        self.assertIn('RestartPreventExitStatus=\n', unit)
        self.assertIn('SuccessExitStatus=\n', unit)
        self.assertIn('TimeoutStartSec=45', unit)
        self.assertIn('Wants=biometryd.service', ui)
        self.assertNotIn('Requires=biometryd.service', ui)
