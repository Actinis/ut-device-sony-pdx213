#!/usr/bin/python3
"""Exercise route transitions and recovery with a fake HAL, without calls/audio."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import sys

source = Path(sys.argv.pop(1)) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'overlay/usr/local/lib/utxperia/call_audio.py'
spec = importlib.util.spec_from_file_location('call_audio', source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Audio:
    def __init__(self):
        self.current = 'dualmic'
        self.sets = []
        self.ignore = False

    def get_parameters(self, key):
        return key + '=' + self.current

    def set_parameters(self, value):
        self.sets.append(value)
        if not self.ignore:
            self.current = value.split('=', 1)[1]


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'state.json'
        self.route = module.VoiceRoute(self.path)
        self.audio = Audio()

    def test_call_end_and_repeated_notifications(self):
        self.route.update(self.audio, False)
        self.route.update(self.audio, True)
        self.route.update(self.audio, True)
        self.route.update(self.audio, False)
        self.assertEqual(self.audio.sets, ['fluence=none', 'fluence=dualmic'])
        self.assertFalse(self.path.exists())

    def test_restart_recovers_owned_state(self):
        self.route.update(self.audio, True)
        restarted = module.VoiceRoute(self.path)
        restarted.update(self.audio, True)
        restarted.update(self.audio, False)
        self.assertEqual(self.audio.current, 'dualmic')
        self.assertFalse(self.path.exists())

    def test_external_change_is_preserved(self):
        self.route.update(self.audio, True)
        self.audio.current = 'quadmic'
        self.route.update(self.audio, False)
        self.assertEqual(self.audio.current, 'quadmic')

    def test_original_none_is_not_owned(self):
        self.audio.current = 'none'
        self.route.update(self.audio, True)
        self.route.update(self.audio, False)
        self.assertEqual(self.audio.sets, [])
        self.assertFalse(self.path.exists())

    def test_failed_set_retries_and_preserves_recovery(self):
        self.audio.ignore = True
        with self.assertRaises(RuntimeError):
            self.route.update(self.audio, True)
        self.assertTrue(self.path.exists())
        self.audio.ignore = False
        self.route.update(self.audio, True)
        self.route.update(self.audio, False)
        self.assertEqual(self.audio.current, 'dualmic')

    def test_unknown_hal_response_is_not_changed(self):
        self.audio.current = 'unsupported'
        with self.assertRaises(ValueError):
            self.route.update(self.audio, True)
        self.assertEqual(self.audio.sets, [])

    def test_hold_and_call_setup_states_are_covered(self):
        self.assertTrue({'active', 'held', 'dialing', 'alerting', 'incoming', 'waiting'} <= module.CALL_STATES)
        self.assertNotIn('disconnected', module.CALL_STATES)


if __name__ == '__main__':
    unittest.main()
