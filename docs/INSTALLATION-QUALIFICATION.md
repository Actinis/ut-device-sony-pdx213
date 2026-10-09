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

Before first installable release:

- Resolve vendor source rebuild/distribution and independently acquired Sony OEM.
- Qualify installation after a documented complete stock Android restoration.
- Test the exact source-import build, first setup, repeated cold boots and slot success.
- Verify recovery after interrupted flashing and restoration to stock firmware.
- Complete hardware, battery/deep-sleep and modem qualification.
- Review exact commands, image sizes, checksums and destructive boundaries.

No universal Installer or OTA is available. A build does not prove installation
or restoration safety; the other variants and slot B remain unqualified.
