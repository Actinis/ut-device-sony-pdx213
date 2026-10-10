# First installable XQ-BT52 candidate

Ubuntu Touch 24.04 Noble, experimental community port. XQ-BT52 and slot A are the
only device/slot under qualification. No universal Installer or OTA channel.

A release candidate must identify the exact device/kernel commits, source lock,
CI run, packaging tool hashes, vendor build report/image, OEM decoded image,
boot/DTBO/userdata/vbmeta checksums and terminal flashing instructions. OEM is
obtained independently by the owner and excluded from public CI/release assets.
Private qualification SSH, saved networks, machine identities, setup completion,
fingerprints, coordinates, photos, recordings and raw phone logs are excluded.

## Technical acceptance

- Verify independent CI output against the exact clean checkout, lock and all
  required artifacts, including matching kernel modules and helper libraries.
- Assemble clean ext4 userdata; validate filesystem, RAW-only sparse encoding,
  privacy cleanup and empty radio-owned oFono storage.
- Flash the exact complete bundle on the documented firmware baseline, compare
  image bytes read back from all written partitions and complete the native
  setup wizard. Boot is written last; never format populated userdata afterward.
- Reboot without manual repairs; verify setup persistence, Wi-Fi reconnection,
  MTP startup, absence of development USB gateway/DNS and mobile-data startup
  with a physically present SIM. Exercise both network switching directions.
- Verify stock camera video stop/main/front stills, full media decoding,
  speaker/microphone tone round-trip, MTP file round-trip and live sensor streams.
- Separately qualify calls/SMS, GNSS fixes in Morph, NFC/card protocols,
  fingerprint unlock/rejection, physical wake gestures and overnight sleep/drain
  on the final source-vendor candidate. Component service startup alone is not
  hardware qualification. IPv6 requires a usable IPv6 test network.
- Qualify installation following complete stock restoration, interrupted-flash
  recovery and actual restoration to stock. Retained Android 12 system metadata
  is provenance, not a complete firmware-baseline restoration test.

## Full CI input

The full-userdata stage exists but currently requires a publicly downloadable,
SHA256-pinned vendor entry with explicit redistribution approval in the lock.
The source-built vendor is a local qualification input; that flag is not set by
successful compilation or phone tests. The Android vendor workflow also needs a
trusted dedicated `ut-pdx213-vendor` runner for its larger source tree. Kernel/boot
CI success does not mean the full-userdata stage ran.

The first proposed tag should describe an experimental installation candidate
for the qualified XQ-BT52 baseline. Create it only after the exact candidate and
remaining limitations are reviewed; no installable release/tag is created by
this checklist.
