# Ubuntu Touch community build publication

Ubuntu Touch OS series, port revision and build number are independent. The source lock currently pins a rootfs in **24.04-2.x** (Noble); publication reads the series from that exact build's locked rootfs entry, not from the latest branch state.

## Development builds

A successful `Noble kernel and boot build` run from `main` automatically publishes a public experimental GitHub prerelease. The `daily` label follows the UT development-channel convention; here builds are produced on relevant pushes or manual build runs, not on a daily timer. This GitHub feed is not an official UBports system-image/OTA channel.

Tag: `pdx213-ut24.04-2.x-daily-<run-id>-<attempt>-<commit>`.
Title: `Xperia 10 III — UT 24.04-2.x — daily build <run-id>.<attempt>`.

Each run has a unique immutable release. It does not become GitHub's Latest release. Existing assets are never overwritten; duplicate publication fails explicitly. Incomplete uploads remain drafts for inspection. Retry a failed build to obtain a new build attempt, or resolve an incomplete draft manually before retrying publication.

## Versioned port releases

Pushing `pdx213-noble-port-v0.1.0` (example) triggers the kernel/boot build and creates a **draft prerelease candidate**. The tag must still resolve to the built commit. Port version `0.1.0` is independent of the UT rootfs version. Review these exact outputs and device results before manually publishing the draft. Do not call a kernel/boot-only candidate a complete installable release.

## Assets and validation

Releases include separately named boot and DTBO images, a kernel/boot tar archive with modules and helpers, build-report, input identity, exact source lock, release-manifest and SHA256SUMS. Download all assets to one directory and run `sha256sum -c SHA256SUMS`. The manifest records OS series, exact rootfs version, source commits, build ID, source workflow URL, port version (null for development snapshots) and pending qualification.

The publisher accepts only successful push/manual runs of the expected build workflow in this repository, on main or explicit version tags. It verifies the downloaded inventory, hashes, modes, required modules and metadata against the source lock retrieved at the exact built commit. Compilation has read-only permissions; the separate publisher alone has contents-write permission. No PAT or private build inputs are needed.

The `Publish Ubuntu Touch build` workflow can also be run manually on main with a successful build run ID. It publishes that run's outputs without rebuilding or relabeling them as a different source revision.

## Installation release gates

Vendor/OEM, userdata, automatic flashing and OTA are excluded. Independently reproducible vendor/OEM inputs, complete stock-baseline installation/restoration and exact-build hardware qualification still gate a complete installation release. Preserve licences and never upload personal backups or private logs.

Actions artifacts expire after 30 days. Release assets are kept until explicitly removed; no automatic historical-release deletion is configured.
