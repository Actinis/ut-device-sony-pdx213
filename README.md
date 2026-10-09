# Ubuntu Touch device adaptation: Sony Xperia 10 III

Target: **Ubuntu Touch 24.04 (Noble)** on Sony Xperia 10 III, codename `pdx213` / `lena`. The initial development target is XQ-BT52; other variants are not qualified.

This repository is reserved for device configuration, rootfs overlays, boot integration, image packaging, build instructions and hardware support documentation.

## Status

Preparation scaffold only. The working port is undergoing fixes in a separate workspace; its sources and validation results have not been imported here. There are no installation instructions or downloadable device images in this repository yet.

The existing development installation uses a device-specific legacy storage layout. A general installation procedure must be developed and qualified separately before publishing instructions for other phones.

## Related repositories

- [Port catalog](https://github.com/Actinis/ut-ports)
- [Ubuntu Touch Sony kernel](https://github.com/Actinis/ut-kernel-sony-msm)

Only Ubuntu Touch 24.04 is currently planned for support. Source import must preserve component provenance and licenses, document exact dependencies and exclude private device data.

This is an Actinis community port, not an official UBports release.
