#!/usr/bin/python3
"""Use the working single-mic voice route only while oFono has calls.

Never capture audio or log telephone numbers. Preserve the original Fluence
mode in the user's runtime directory, including across a helper restart.
"""
import json
import os
from pathlib import Path
import signal

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

CALL_STATES = frozenset(('dialing', 'alerting', 'incoming', 'waiting', 'active', 'held'))
MODES = frozenset(('none', 'dualmic', 'quadmic'))


class VoiceRoute:
    def __init__(self, state_file):
        self.path = Path(state_file)
        self.baseline = None
        if self.path.exists():
            saved = json.loads(self.path.read_text())['baseline']
            if saved not in MODES - {'none'}:
                raise ValueError('Invalid saved Fluence mode')
            self.baseline = saved

    def mode(self, audio):
        value = str(audio.get_parameters('fluence'))
        if not value.startswith('fluence=') or value[8:] not in MODES:
            raise ValueError('Unsupported Fluence response')
        return value[8:]

    def update(self, audio, in_call):
        current = self.mode(audio)
        if in_call:
            if current == 'none':
                return
            if self.baseline is None:
                self.baseline = current
                stage = self.path.with_suffix('.tmp')
                stage.write_text(json.dumps({'baseline': current}))
                stage.chmod(0o600)
                stage.replace(self.path)
            audio.set_parameters('fluence=none')
            if self.mode(audio) != 'none':
                raise RuntimeError('Voice route was not applied')
            print('utxperia-call-audio: single-mic voice route active', flush=True)
        elif self.baseline is not None:
            # Restore only the value this helper owns; preserve external changes.
            if current == 'none':
                audio.set_parameters('fluence=' + self.baseline)
                if self.mode(audio) != self.baseline:
                    raise RuntimeError('Original Fluence mode was not restored')
            self.path.unlink(missing_ok=True)
            self.baseline = None
            print('utxperia-call-audio: original Fluence mode restored', flush=True)


def main():
    DBusGMainLoop(set_as_default=True)
    runtime = os.environ['XDG_RUNTIME_DIR']
    route = VoiceRoute(Path(runtime) / 'utxperia-call-audio.json')
    system = dbus.SystemBus()
    loop = GLib.MainLoop()
    last_error = None

    def audio_interface():
        peer = dbus.connection.Connection('unix:path=' + runtime + '/pulse/dbus-socket')
        obj = peer.get_object(None, bytes.fromhex('2f6f72672f7361696c666973686f732f617564696f73797374656d706173737468726f756768').decode('ascii'))
        return peer, dbus.Interface(obj, bytes.fromhex('6f72672e5361696c666973684f532e417564696f53797374656d506173737468726f756768').decode('ascii'))

    def refresh(*unused):
        nonlocal last_error
        peer = None
        try:
            states = []
            manager = dbus.Interface(system.get_object('org.ofono', '/'), 'org.ofono.Manager')
            for path, props in manager.GetModems():
                if 'org.ofono.VoiceCallManager' not in props.get('Interfaces', []):
                    continue
                vm = dbus.Interface(system.get_object('org.ofono', path), 'org.ofono.VoiceCallManager')
                states.extend(str(p.get('State', '')) for _, p in vm.GetCalls())
            peer, audio = audio_interface()
            route.update(audio, any(s in CALL_STATES for s in states))
            last_error = None
        except (dbus.DBusException, OSError, ValueError, RuntimeError) as error:
            description = type(error).__name__
            if description != last_error:
                print('utxperia-call-audio: waiting for audio/telephony (' + description + ')', flush=True)
                last_error = description
        finally:
            if peer is not None:
                peer.close()
        return True

    def changed(*unused):
        def once():
            refresh()
            return False
        GLib.idle_add(once)

    for member in ('CallAdded', 'CallRemoved'):
        system.add_signal_receiver(changed, signal_name=member, dbus_interface='org.ofono.VoiceCallManager')
    system.add_signal_receiver(changed, signal_name='PropertyChanged', dbus_interface='org.ofono.VoiceCall')
    system.add_signal_receiver(changed, signal_name='NameOwnerChanged',
                               dbus_interface='org.freedesktop.DBus', arg0='org.ofono')
    signal.signal(signal.SIGTERM, lambda *args: loop.quit())
    signal.signal(signal.SIGINT, lambda *args: loop.quit())
    GLib.timeout_add_seconds(2, refresh)
    refresh()
    try:
        loop.run()
    finally:
        peer = None
        try:
            peer, audio = audio_interface()
            route.update(audio, False)
        except (dbus.DBusException, OSError, ValueError, RuntimeError):
            pass  # Runtime state allows the next instance to complete restoration.
        finally:
            if peer is not None:
                peer.close()


if __name__ == '__main__':
    main()
