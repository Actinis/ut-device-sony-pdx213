# Ubuntu Touch 24.04 — Sony Xperia 10 III

Experimental Actinis community adaptation for **Ubuntu Touch 24.04 Noble**,
Halium 11, Sony `pdx213` / `lena`. The qualified prototype variant is **XQ-BT52**;
other variants are untested. This is not an official UBports release.

Sources include independent GPT-label boot/storage integration, a Noble rootfs
overlay, native Android hardware services, kernel/boot builds and local image
assembly. The runtime prototype boots from ordinary ext4 userdata with separate
Ubuntu, Android and vendor images.
Vendor is available as a pinned public build input; its publication scope and
unresolved licence clarification are documented in [VENDOR.md](docs/VENDOR.md). Installation after
complete stock Android restoration remains unqualified. A complete local source-vendor candidate has
passed clean installation, first setup, normal reboot, Wi-Fi, MTP, camera,
microphone tone tests and sampled sensor streams; see the exact scopes below.
Do not apply prototype storage assumptions to other models or firmware revisions.

There is no universal UBports Installer integration, complete installation release or
OTA channel. Successful main builds are published as experimental kernel/boot prereleases; version tags create draft candidates. See [publication rules](docs/RELEASING.md).

- [Build and local data layout](docs/BUILD.md)
- [Exact sources and manual inputs](docs/SOURCES.md)
- [Hardware results and gaps](docs/HARDWARE.md)
- [Installation qualification](docs/INSTALLATION-QUALIFICATION.md)
- [Release preparation](docs/RELEASING.md)
- [Acceptance before a complete installation release](docs/RELEASE-CANDIDATE.md)

CI validates source metadata and tests, and the build workflow compiles the
kernel, DTBO, helpers, boot and full userdata candidates from the pinned sources.
Sony OEM is obtained separately. CI does not flash
or qualify a phone. Device results describe the tested prototype; source-import
builds require their own installation/hardware qualification.

Related: [port catalog](https://github.com/Actinis/ut-ports),
[kernel source branch](https://github.com/Actinis/ut-kernel-sony-msm/tree/main).

GNSS assistance, privacy and current qualification limits: [GNSS](docs/GNSS.md).

NFC build inputs, supported operations and explicit qualification gaps:
[NFC](device/nfc/README.md).

Double-tap wake control and qualification: [touch wake](docs/TOUCH.md).

Experimental lift wake integration and qualification: [Raise to wake](device/repowerd/README.md).

The [full CI verification report](evidence/full-ci.json) confirms independent
GitHub-hosted assembly and verification of the downloaded boot, DTBO, userdata
and vbmeta candidate. Sony OEM is excluded. This is build evidence; these exact
CI images have not yet been qualified by flashing them to a phone.
