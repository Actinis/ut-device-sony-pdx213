# Raise to wake on XQ-BT52

The Noble image builds Repowerd from UBports commit
`36575160752bdd0a983bee1b53e041ccc4ceaa60` with `raise-to-wake.patch`.
Upstream authorship and GPL-3.0 notices are retained; see `UPSTREAM-COPYRIGHT`.
`inputs.json` pins the source, patch and every development package by exact
version, URL and SHA256. Runtime libraries come from the locked Noble rootfs;
no connected-phone library is a build input. The builder uses the locked NDK
r23b compiler, GNU C++ 13 development headers and upstream `ENABLE_WERROR=OFF`.
Baseline Clang warnings prevent an all-warnings-as-errors claim.

Android's `sns_tilt Wakeup` type-22 sensor feeds SensorFW's existing
`wakeupsensor`. Repowerd receives timestamp-checked wake-only activity:
it turns on an off display without toggling or extending an already-on display.
An active call or Repowerd's current proximity-near state suppresses this event.
Proximity may be stale; this is not a qualified pocket-rejection mechanism.

The package installs `/usr/local/libexec/utxperia-repowerd` and a service
drop-in enabling `REPOWERD_RAISE_TO_WAKE=1`; the distribution's
`/usr/sbin/repowerd` remains intact. There is currently no UI toggle.
SensorFW selects type 22 through `98-utxperia-raise.conf`.

`utxperia-tilt.service` prepares recognition before the Android container starts.
It reads the device's existing `sns_tilt` registry, validates the fields,
preserves unknown fields and angle threshold, and changes only sampling to
25 Hz and the initial/recognition windows to 0.3/0.4 seconds. It bind-mounts
the generated file from `/var/lib/utxperia/tilt/` over the registry path.
It never writes the factory file or remounts persist writable. Missing registry
skips the unit; invalid registry fails it without blocking Android startup.
The timings are qualified only for the tested XQ-BT52 vendor sensor implementation.

## Qualification

The owner confirmed fast physical lift wake with the screen remaining on using
the native Repowerd implementation and these timings. The host core suite passed
334 tests, including five new cases for off/on behavior, display timeout,
proximity state and active calls. These tests exclude the separate performance
booster target and do not simulate the physical sensors. The build runs this
suite before compiling ARM64 Repowerd. Binary/report are mandatory packaging
artifacts, covered by the main build identity and artifact hashes.

Cold boot of the assembled image, deep suspend, false positives/pocket behavior,
battery impact, SensorFW restart recovery and long-duration reliability remain
unqualified. Full upstream adapter/integration tests have not been run.
No battery-consumption claim follows from the HAL's nominal power value.

To disable this experimental feature, remove only `utxperia-raise.conf` from
the Repowerd drop-ins and only `98-utxperia-raise.conf` from SensorFW configuration,
disable `utxperia-tilt.service`, reload systemd and reboot. This returns to the
packaged daemon and original registry; retain other port service drop-ins.
