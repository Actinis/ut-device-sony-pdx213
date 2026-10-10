# Source-built Android vendor input

The packaging input is [pdx213-vendor-aosp11-001](https://github.com/Actinis/ut-device-sony-pdx213/releases/tag/pdx213-vendor-aosp11-001).
The raw image, versioned URL, byte size and SHA256 are pinned in `sources.lock.json`.
Its independently pinned `build_report` is a required external input: CI verifies
image and report hashes, the source manifest, container/builder identities and
all patched and unpatched project commits before userdata assembly. Reports
are retained in the full candidate archive. The unchanged upstream NOTICE is
published with the vendor. Sony OEM and private phone data are excluded.

Publication was explicitly authorized by the port maintainer. The lock's
`redistribution_approved` flag records that publication authorization; it does
not assert a Sony grant or completion of a legal review. Clarification of nine
Sony audio-calibration files remains [open](https://github.com/sonyxperiadev/device-sony-pdx213/issues/10).
The source/module licence audit is partial; upstream licences remain applicable.
See [origin audit](../evidence/vendor-origin-audit.json).

`manifest.xml` pins 733 public AOSP/Sony projects including the Android patch
repository at `f683f1fb0ab85e4e2247ef6ed4910440205b1e98`. The builder checks clean
base commits, checks the complete 17-patch series in disposable worktrees,
applies it once with original authorship and deterministic commit dates, and
records every resulting project commit. Reusing prepared sources requires the
same recipe and clean commits. No phone backup, OEM image or private credential
is mounted into the build container.

## Local source build

Use a dedicated Linux x86_64 machine with Docker, adequate RAM and at least
300 GiB free disk for the Android tree and output. Source and output directories
must be separate. Obtain a repo launcher from the locked git-repo source; the
checkout's repo implementation must match `repo_tool` in the lock.

```sh
export UT_PORTS_DATA_DIR=/path/to/ut-ports-data
python3 tools/build_vendor.py --sync --prepare-only \
  --repo-launcher /path/to/repo-launcher \
  --android-source "$UT_PORTS_DATA_DIR/builds/pdx213/vendor-001/android" \
  --output "$UT_PORTS_DATA_DIR/builds/pdx213/vendor-001/output" --jobs 8

docker build --build-arg BUILD_UID="$(id -u)" --build-arg BUILD_GID="$(id -g)" -t ut-pdx213-vendor device/vendor
vendor_image=$(docker image inspect ut-pdx213-vendor --format '{{.Id}}')
python3 tools/build_vendor.py \
  --android-source "$UT_PORTS_DATA_DIR/builds/pdx213/vendor-001/android" \
  --output "$UT_PORTS_DATA_DIR/builds/pdx213/vendor-001/output" \
  --container-engine /path/to/docker --container-image "$vendor_image" --jobs 8
```

Container package revisions are recorded, but apt repositories are not snapshot
pinned. The base-image digest, source commits, patches and recipe files are
locked; bit-identical output is not yet claimed. The normal GitHub-hosted
kernel runner is not provisioned for this Android source build. A dedicated vendor builder is required only when rebuilding vendor itself;
normal full-image CI uses the published immutable vendor input.

## Full-image CI

GitHub-hosted CI downloads this vendor and its build report, then assembles
boot, DTBO, userdata and vbmeta with checksum-covered flashing/OEM preparation
instructions. No dedicated runner is needed for this path. Actual CI success,
installation qualification and public installation releases are separate facts;
see [installation evidence](INSTALLATION-QUALIFICATION.md).

The optional Android-source workflow uses the dedicated `ut-pdx213-vendor`
runner labels and `UT_VENDOR_DATA_DIR`. It needs 300 GiB free and Docker; no
matching runner is configured. It is not required to assemble full images from
the published vendor input.

The exact image passed local XQ-BT52 clean installation, setup, reboot, Wi-Fi,
MTP, stock Camera video/main/front stills, both microphone tone tests and selected
SensorFW streams. Other hardware and firmware-baseline scopes remain explicit
in the installation evidence. Bit-identical rebuilding is not claimed.
