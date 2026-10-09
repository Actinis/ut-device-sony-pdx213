# Cellular call audio

Sony exposes Qualcomm IQcRilAudio slot1 and slot2 callbacks. The supplemental
ofono/ril_subscription.d/utxperia-qti-audio.conf supplies both names to the
QTI audio helper; telephony uses binder.conf and excludes the legacy RIL plugin.
Both QTI and AF audio helpers run only in the phablet user session, preventing
administrative sessions from replacing phone callbacks.

utxperia-call-audio monitors oFono call states without recording speech or
logging phone numbers. During setup, active calls and holds, it selects the
single-microphone fluence=none route, then restores the prior route on call end.
Runtime state supports recovery after a helper restart. External changes are
preserved and unsupported HAL responses rejected. Dual-microphone call noise
processing remains unqualified; modem firmware and calibration are unchanged.

Seven fake-HAL tests cover transitions, recovery, external changes, failed
writes and unsupported responses: python3 tools/test_call_audio.py.
On the XQ-BT52 prototype, calls and SMS worked in both directions. Bidirectional
audio through the earpiece and speakerphone was confirmed after reboot, and the
original dualmic route returned after hangup. VoLTE, SIM2 and
Bluetooth HFP remain unqualified. See HARDWARE.md.
