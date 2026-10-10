# Independent Android vendor candidate

The working port currently accepts the qualified manual vendor hash in
`sources.lock.json`. A new vendor is not qualified simply because it compiles.
The public source recipe under `device/vendor/` is an independent candidate,
not a claim that its bytes match the current manual input.

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
kernel runner is not provisioned for this Android source build. A dedicated
vendor builder or independently reviewed public vendor artifact is required.

## Promotion to full CI

The kernel workflow has a full userdata packaging stage. It remains disabled
while `vendor.kind` is `manual`. Promotion requires a separately reviewed public
artifact URL, exact hash/version and `redistribution_approved: true` in the
artifact entry. This must follow source/licence inventory review and device
qualification, not merely an upload of the manual prototype image.

Full candidate assembly verifies the kernel report, dependency identities and
mandatory modules/helpers. It retains boot, DTBO, userdata, vbmeta and assembly
metadata in a separate Actions artifact. Sony OEM is excluded. The existing
kernel/boot publisher does not turn this candidate into an installable release.
Clean installation from the documented stock firmware baseline and restoration
remain release gates.

The manual `Android vendor source candidate` workflow uses runner labels
`self-hosted`, `linux`, `x64`, `ut-pdx213-vendor` and repository variable
`UT_VENDOR_DATA_DIR`. It requires 300 GiB free and Docker access. No matching
runner is currently configured. It uploads source/build reports only, never
unreviewed vendor bytes.

## Verified host candidate

The pinned recipe has completed a local source build: 733 projects and all
17 patches were checked. The raw vendor image is 106,520,576 bytes and the
sparse image is 56,123,504 bytes. Input/output hashes and the container identity
are recorded in [the host evidence](../evidence/vendor-source-build.json).
This does not claim bit-identical rebuilding or a successful phone boot.

Read-only comparison found all qualified vendor paths present, 285 file-content
differences, unchanged symlink targets and 241 permission/ownership differences.
The new image needs its own hardware qualification. Legacy PN54x/PN55x NXP
firmware blobs are absent. All nine ACDB/calibration files match the pinned
public Sony device tree, but none appears in the generated NOTICE mapping.
Their distribution terms must be resolved before approving a public vendor
artifact; public Git hosting alone is not recorded as distribution approval.

The qualified manual vendor remains the packaging input. The source candidate
has not replaced it, been flashed, or been uploaded as a public binary.
