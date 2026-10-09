# Locked inputs and build scope

Only Ubuntu Touch 24.04 Noble is supported. `sources.lock.json` schema 2 is
validated by `tools/sources_lock.py`, CI, the build and release metadata tool.
`locked` means that the listed input identities are pinned, not that all inputs
are downloadable or a complete installation has been reproduced.

| Kind | Contract |
| --- | --- |
| git | HTTPS URL and full commit; kernel gitlinks additionally pin WLAN/techpack/WireGuard sources |
| artifact | HTTPS URL, version, filename and SHA256; reject a changed asset even if its URL/tag remains the same |
| manual | Version, reference URL, SHA256, acquisition instructions and redistribution restrictions; never automatically download or publish |
| derived | Dependencies and recipe description; tracked boot metadata and helper sources also have SHA256 |

The inventory covers the kernel, Noble rootfs build 121, Halium 11 GSI build
1575, Halium dynparts initrd, NDK r23b and mkbootimg. DTB/DTBO are generated
from the kernel, not supplied from a phone. Boot metadata are tracked Sony
parameters. The static reboot helper and vendor-manager shim are compiled from
tracked sources; the shim targets Android API 30. Boot ext4 utilities and their
ELF dependencies come from the pinned Ubuntu rootfs, including the package
versions recorded in `rootfs_tools`.

Kernel provenance and all nine submodule commits are also recorded in the
kernel repository's `docs/UPSTREAM.json`. AppArmor is already present there;
no build-time backport or patch application is required.

## Manual inputs and limits

The vendor image is a mer-hybris/Jolla-built Android 11 AOSP adaptation. Its
exact SHA256 is pinned, but an independent source rebuild and a publicly
obtainable byte-equivalent artifact have not been established. No installed
legacy filesystem or activation is needed by the runtime; this does not make
the vendor input independently reproducible. The reviewed Android source
manifest and vendor notices are under `notices/`; do not infer that these alone
complete the source or redistribution audit.

Sony Android 11 / 4.19 / v9a Lena OEM is obtained by the user directly from
Sony under its EULA. It is never included in Git or automatic CI. The lock
records the qualified prototype's OEM ext4-image hash, not the public ZIP's
hash. Equivalence of an independently downloaded Sony image remains unqualified.
A complete image release is gated on resolving these inputs and their licences.

Host utilities also affect byte-level image reproducibility: GNU make, tar,
Python, QEMU, fakeroot, mksquashfs, e2fsprogs, Android libsparse and avbtool.
The CI OS is Ubuntu 24.04; package revisions are currently supplied by its
repositories, not a hermetic container digest. Local assembly records the
explicit utility binary hashes in `assembly-report.json`. A pinned host build
environment is still required before claiming bit-identical full images.

No personal keys, device serials, modem identities, backups, private payloads,
raw device logs, OEM/vendor binaries or extracted Android/Ubuntu images are
source inputs in Git. Runtime camera patching uses hash-checked owner-supplied
OEM bytes; the repository contains only the guard implementation.
