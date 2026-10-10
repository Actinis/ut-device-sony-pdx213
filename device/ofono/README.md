# Radio screen-off indication filter

The Noble build compiles ofono-binder-plugin 1.1.33 against the exact locked
rootfs libraries and ARM64 development packages. Source and package URLs,
commits and SHA256 values are in `inputs.json`. The original upstream licence
and UBports MTK patch authorship are retained. The packaging repository's other
patches only change its Makefile/Debian workflow; this builder compiles the C
sources directly and retains the MTK source patch.

`screen-off-filter.patch` restores display-dependent filtering lost in upstream
commit aeb396b9c79cfa8aa1d838f5268fb324ca411bcb. Screen on uses the interface's
full filter; screen off retains DATA_CALL_DORMANCY. This avoids repeated signal
and cell-information wakeups while keeping radio data-state indications. Voice
and SMS delivery are not controlled by this indication filter.

On XQ-BT52, fixed/control/fixed comparisons without USB measured approximately
93%, 52%, and 94% time in suspend respectively over short windows. The fixed
package was installed and survived reboot; modem registration and an active
data context were observed. These measurements do not qualify overnight drain,
incoming calls/SMS during prolonged suspend, or a freshly flashed CI image.

The normal rootfs packager replaces the distribution plugin at
its distribution plugin path; no debug service or polling workaround
is shipped. The binary and its build report are mandatory packaging inputs.
The locked rootfs retains package licences; additional upstream licence files
are retained under `/usr/share/doc/utxperia-ofono/`.
