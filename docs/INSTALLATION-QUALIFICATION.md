# Installation qualification

Only the XQ-BT52 prototype with unlocked bootloader
`1322-1665_X_Boot_SM6350_LA2.0.1_S_108` and slot A is qualified. Runtime storage
is ordinary ext4 userdata, resolved by GPT labels. It contains a Ubuntu squashfs,
Halium Android image, separate vendor image and writable overlay/userdata.
OEM, modem, Bluetooth, DSP and persist are mounted by partition label.
No GPT, TA, calibration, persist or bootloader rewrite is part of the recipe.

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

The local candidate assembled from exact CI run [38079924323](https://github.com/Actinis/ut-device-sony-pdx213/actions/runs/38079924323)
was flashed after erasing userdata. It uses the locked manual vendor and a
separately acquired official Sony v9a OEM. The three-GiB seed expanded on first
boot; the native setup wizard completed and Wi-Fi connected using a password
provided only after flashing. Stock Camera recorded and stopped video with
audio, captured main-camera and front-camera JPEGs, and switched cameras in the
same process. Media were fully decoded privately. A normal system reboot retained wizard
completion and automatically reconnected Wi-Fi with the main services active.

For autonomous qualification only, a private key-only USB SSH service was added
to the writable overlay after image readback. It is absent from the distributed
source/image inputs. Runtime qualification therefore includes this diagnostic
overlay. See [sanitized evidence](../evidence/installation-candidate.json).

The OEM, userdata, DTBO and vbmeta image prefixes were read back with matching
checksums before first boot. A coherent offline userdata backup was compared
with the original filesystem, extracted and checked as a restored ext4 image
on the host. Actual stock restoration and interrupted-flash recovery remain
unqualified. Firmware partitions were retained; this is not a complete stock
Android baseline test or approval for a public full-image release.

Before first installable release:

- Resolve vendor distribution and complete source-vendor qualification; independently acquired OEM flashing/readback and local first boot passed (see OEM.md).
- Qualify installation after a documented complete stock Android restoration.
- Complete repeated cold boots and slot success qualification; exact CI candidate flashing and first setup passed.
- Verify recovery after interrupted flashing and restoration to stock firmware.
- Complete hardware, battery/deep-sleep and modem qualification.
- Review exact commands, image sizes, checksums and destructive boundaries.

No universal Installer or OTA is available. A build does not prove installation
or restoration safety; the other variants and slot B remain unqualified.
