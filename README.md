# Ubuntu Touch 24.04 — Sony Xperia 10 III

Experimental Actinis community adaptation for **Ubuntu Touch 24.04 Noble**,
Halium 11, Sony `pdx213` / `lena`. The qualified prototype variant is **XQ-BT52**;
other variants are untested. This is not an official UBports release.

Sources include independent GPT-label boot/storage integration, a Noble rootfs
overlay, native Android hardware services, kernel/boot builds and local image
assembly. The runtime prototype boots from ordinary ext4 userdata with separate
Ubuntu, Android and vendor images.
An independently reproducible vendor input and an installation after complete
stock Android restoration are still unqualified. Do not apply prototype storage
assumptions to other models or firmware revisions.

There is no universal UBports Installer integration, complete installation release or
OTA channel. Successful main builds are published as experimental kernel/boot prereleases; version tags create draft candidates. See [publication rules](docs/RELEASING.md).

- [Build and local data layout](docs/BUILD.md)
- [Exact sources and manual inputs](docs/SOURCES.md)
- [Hardware results and gaps](docs/HARDWARE.md)
- [Installation qualification](docs/INSTALLATION-QUALIFICATION.md)
- [Release preparation](docs/RELEASING.md)

CI validates source metadata and tests, and the build workflow compiles the
kernel, DTBO, helpers and boot image from the pinned sources. It does not flash
or qualify a phone. Device results describe the tested prototype; source-import
builds require their own installation/hardware qualification.

Related: [port catalog](https://github.com/Actinis/ut-ports),
[kernel source branch](https://github.com/Actinis/ut-kernel-sony-msm/tree/main).

GNSS assistance, privacy and current qualification limits: [GNSS](docs/GNSS.md).

NFC build inputs, supported operations and explicit qualification gaps:
[NFC](device/nfc/README.md).

Double-tap wake control and qualification: [touch wake](docs/TOUCH.md).

Experimental lift wake integration and qualification: [Raise to wake](device/repowerd/README.md).
