# Installation qualification

Only the XQ-BT52 prototype with unlocked bootloader
`1322-1665_X_Boot_SM6350_LA2.0.1_S_108` and slot A is qualified. Runtime storage
is ordinary ext4 userdata, resolved by GPT labels. It contains a Ubuntu squashfs,
Halium Android image, separate vendor image and writable overlay/userdata.
OEM, modem, Bluetooth, DSP and persist are mounted by partition label.
No GPT, TA, calibration, persist or bootloader rewrite is part of the recipe.

Read-only inspection of the retained `super` system partition reports stock
Android 12, Sony build `62.1.A.0.533`. This is retained-system provenance, not
proof that every firmware partition belongs to that build or that a fresh stock
restoration has been tested. Halium/AOSP 11 identifies the adaptation base; it
is not a requirement to downgrade the stock operating system to Android 11.
Other stock firmware baselines remain unqualified. See
[firmware evidence](../evidence/retained-stock-system.json).

The prototype has an ext4 clean-install test with fastboot transfers limited to
128 MiB, RAW rather than large FILL sparse chunks, a three-GiB seed filesystem
and first-boot expansion to its actual userdata partition. Its measured storage
capacity is not a requirement or a partition map for another phone. Installation
is destructive to userdata. Existing storage layouts must not be assumed
compatible with the ext4 payload.

The development fastboot sequence for this exact baseline writes owner-supplied
Sony OEM to oem_a, clears userdata, writes userdata using `fastboot -S 128M`,
writes dtbo_a, verification-disabled vbmeta_a and vbmeta_system_a, then boot_a.
These are qualification details, not generalized installation approval. Do not
apply `fastboot -w` after installing the populated userdata image.

## Current complete local candidate

The local source-vendor candidate assembled from exact CI run
[38089144991](https://github.com/Actinis/ut-device-sony-pdx213/actions/runs/38089144991)
was flashed after erasing userdata. Its source-vendor input is explicitly pinned
by image and build-report hashes; Sony v9a OEM was acquired separately. The
three-GiB seed expanded on first boot and the native setup wizard completed.
Stock Camera recorded and stopped video with audio and captured main/front
JPEGs in the same process; the complete media were decoded privately. MTP
upload/download of a synthetic file matched, and the object was removed.

Normal reboot retained setup completion and reconnected Wi-Fi. IPv4 mobile data
worked after first setup and after switching off Wi-Fi following a reboot;
returning to Wi-Fi also worked. MTP remained active without enabling the
development USB gateway or its DNS. Mobile startup after a reboot with Wi-Fi
disabled remains unqualified because the SIM was removed during that test.
IPv6 has not been qualified on a usable IPv6 network.

Speaker test tones were detected by both microphones. Accelerometer, gyroscope,
magnetometer, ambient-light, proximity, rotation and compass produced streams;
this does not establish physical accuracy or wake gestures. Indoor GNSS emitted
satellite/NMEA callbacks without a position fix. Calls/SMS, GNSS in Morph, NFC,
fingerprint, physical wake gestures and overnight battery/sleep require final
source-vendor qualification; earlier component results do not establish these
on this exact complete candidate.

The empty radio-owned oFono storage fix is included in current sources and
survived a runtime reboot. Its pristine current-source image has not yet been
qualified. See [release acceptance](RELEASE-CANDIDATE.md).

For autonomous qualification only, a private key-only USB SSH service was added
to the writable overlay after image readback. It is absent from the distributed
source/image inputs. Runtime qualification therefore includes this diagnostic
overlay. See [sanitized evidence](../evidence/installation-candidate.json).

The OEM, userdata, DTBO and vbmeta image prefixes were read back with matching
checksums before first boot. A coherent offline userdata backup was compared
with the original filesystem, extracted and checked as a restored ext4 image
on the host. One POSIX ACL was unsupported during host extraction; full ACL
restoration is not claimed. Actual stock restoration and interrupted-flash recovery remain
unqualified. Firmware partitions were retained; this is not a complete stock
Android baseline test or approval for a public full-image release.

Before first installable release:

- Resolve vendor distribution and complete remaining source-vendor qualification; independently acquired OEM flashing/readback and local first boot passed (see OEM.md).
- Qualify installation after a documented complete stock Android restoration.
- Complete repeated cold boots and slot success qualification; exact CI candidate flashing and first setup passed.
- Verify recovery after interrupted flashing and restoration to stock firmware.
- Complete hardware, battery/deep-sleep and modem qualification.
- Review exact commands, image sizes, checksums and destructive boundaries.

No universal Installer or OTA is available. A build does not prove installation
or restoration safety; the other variants and slot B remain unqualified.
