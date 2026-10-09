# Xperia cellular call audio

## Observed failures and repair

With a SIM installed, the owner confirmed call establishment and SMS in both
directions. Initial calls had no audio in either direction even though
PulseAudio selected `voicecall` and the earpiece.

The stock `audiosystem-passthrough-qti` user service exited with status 2 because
version 1.3.x reads legacy slot mappings and none identified the two binder
slots. Sony exposes `vendor.qti.hardware.radio.am@1.0::IQcRilAudio/slot1` and
`slot2`. The supplemental `ofono/ril_subscription.d/utxperia-qti-audio.conf`
provides these names to the audio helper; actual telephony continues to use
`binder.conf`, and the legacy RIL plugin remains excluded. The service is enabled
and retries failures. The separate AF helper remains available for multimedia. Both helpers exclude
root user sessions: administrative SSH logins previously started duplicate
helpers that could replace the phone session callback.
The [helper's documentation](https://github.com/droidian/audiosystem-passthrough)
explains Qualcomm IQcRilAudio callbacks and their connection to the audio HAL.

Once callbacks reached the HAL, it received
`vsid=297816064;call_state=2;call_type=GSM` and started `voicemmode1-call`.
The owner then heard the remote phone on Sony, but uplink remained silent.
Reapplying microphone unmute and explicitly unmuting the DSP session did not
repair it. Changing `fluence=dualmic` to `fluence=none` changed the voice input
from `voice-dmic-ef` (ACDB 41) to `handset-mic` (ACDB 4); the owner confirmed
that speech from Sony became audible on the remote phone.

`utxperia-call-audio.service` now monitors oFono call states without recording
speech or logging numbers. It selects `fluence=none` during call setup, active
calls and holds, and restores the original mode when calls end. Runtime state
allows recovery after a helper restart. External changes are preserved on
restoration; unsupported HAL responses are rejected. This uses one microphone
for calls, so Sony's dual-microphone noise processing is not qualified.

## Validation and rollback

Seven fake-HAL tests cover call/end/repeated signals, saved-state recovery,
external changes, original `none`, failed writes, unsupported responses and
setup/hold states. Run `tools/test_call_audio.py` with the installed script on
Ubuntu Touch (Python dbus/GLib dependencies are already present).

Live evidence distinguishes manually confirmed audio from permanent-install
qualification. SMS send/receive and initial bidirectional call audio were
confirmed by the owner. Cold-boot validation is recorded in HARDWARE.md.
VoLTE, second-SIM calls, Bluetooth HFP and carrier combinations remain untested.

To disable the microphone workaround, stop and disable
`utxperia-call-audio.service` in the phablet user session; it restores the original
Fluence mode on a normal stop. The QTI helper should remain enabled for normal
call audio. No modem firmware, calibration or vendor partition is modified.

Final qualification: after reboot, the owner confirmed both directions through
the earpiece and speakerphone and ended the call. oFono reported no remaining
calls; the helper logged activation and restoration, `fluence=dualmic` returned
and runtime override state was removed. Fresh root SSH sessions did not start
duplicate audio helpers. Both QTI and AF helpers belonged to phablet.
