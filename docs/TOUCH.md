# Double-tap wake on XQ-BT52

The Noble boot metadata enables double-tap wake with
`sec_touchscreen.double_tap_to_wake=1`. Repowerd controls the writable
`/sys/module/sec_touchscreen/parameters/double_tap_to_wake` parameter through
the deviceinfo `DoubleTapToWake` setting (`Y` / `N`).

The sec_ts_lena driver keeps the touch sensor powered in its low-power mode
while the display is off. The qualified S6SY761 firmware reports double tap
as gesture subtype 0, ID 15; the driver emits KEY_POWER only when enabled.
The Sony panel power lock is released when the screen resumes.

Enable the setting while the screen is awake. Enabling with a fully powered-off
sensor returns EBUSY. Disabling during low-power mode suppresses gesture wake
immediately; sensor power is released on the next resume/shutdown cycle.
Persistence of a disabled preference across reboot has not been qualified;
the boot metadata defaults to enabled.

## Qualification

On 2026-10-10, the owner confirmed three physical double-tap wake attempts,
that spaced single taps did not wake, and physical double-tap wake after reboot
on the final kernel. Repowerd reported support and its enable/disable controls
passed, including disabling while the sensor was in low-power mode. Five
screen-off/on cycles returned the firmware power-mode register from 01 to 00
without observed I2C or panel-lock errors. Synthetic power-key events were used
for those cycles, not as proof of physical gesture recognition.

The tested kernel was compiled and installed with the existing prototype
ramdisk and modules. A clean full image build from the updated lock and its
installation remain unqualified. Full system suspend, unplugged battery drain,
pocket rejection, other firmware/variants and long-duration use remain untested.

A passive controller trace during the requested single-tap/double-tap sequence
contained one gesture event (subtype 0, ID 15) and no coordinate events.
No distinct single-tap enable command was found in the sec_ts_lena source.
Single-tap wake is therefore not enabled or qualified; this observation does
not rule out undocumented firmware support. No firmware registers were changed
for this passive probe.
