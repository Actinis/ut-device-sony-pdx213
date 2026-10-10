# Release metadata tools

`tools/release_metadata.py` hashes reviewed image files and writes `sources.lock.json`, `release-manifest.json` and `SHA256SUMS` to a new output directory. Images remain in their original directory. SHA256SUMS covers images and both JSON metadata files; distribute them together.

Example after source import and qualification preparation:

```sh
python3 tools/release_metadata.py --images out/images --output out/metadata --lock sources.lock.json --device-commit FULL_COMMIT --tag pdx213-noble-port-v0.1.0 --build-url https://github.com/Actinis/ut-device-sony-pdx213/actions/runs/RUN_ID
```

The tool validates naming and pins, rejects unexpected files, symlinks and empty images, and always marks hardware qualification pending. It cannot determine image bootability or verify the build run remotely. Review provenance and attach qualification results before publishing.

Create a draft manually once artifacts and reviewed notes exist:

```sh
gh release create pdx213-noble-port-v0.1.0 --repo Actinis/ut-device-sony-pdx213 --target FULL_COMMIT --draft --title 'Xperia 10 III Noble port v0.1.0' --notes-file RELEASE_NOTES.md out/images/*.img out/metadata/SHA256SUMS out/metadata/sources.lock.json out/metadata/release-manifest.json
```

Do not run this example until placeholders, pins, installation instructions and actual device results are complete. The draft command is documentation, not an automatic publication workflow.

## Automatic kernel/boot publication

`publish_ci_release.py` implements the verified CI publication path described in [RELEASING.md](RELEASING.md). It reads the original run's exact lock and verifies its archived build identity before preparing assets. It does not use this checkout's dependency pins to relabel an older build.

The earlier `release_metadata.py` remains a local reviewed-image tool; it is not used to publish CI kernel/boot results. Automated development releases use a UT-series/daily-build tag, while version tags retain the port-version convention.

## Local terminal-flashing candidate

`tools/prepare_install_bundle.py` binds an assembled userdata to the exact clean
source checkout, build ID, source lock, complete kernel/helper/module report and
Sony OEM decoded identity. It rejects stale userdata, missing results, changed
images, linked inputs and Sony-incompatible FILL chunks. It never downloads,
flashes or publishes. The output contains concrete slot-A fastboot commands,
checksums and a manifest; it is a local candidate, not redistribution approval.

```sh
export UT_PORTS_DATA_DIR=/path/to/ut-ports-data
python3 tools/prepare_install_bundle.py \
  --source-checkout /path/to/exact-device-checkout \
  --build-id BUILD_ID \
  --oem-fastboot-image /path/to/owner-obtained-oem-raw-sparse.img \
  --output "$UT_PORTS_DATA_DIR/private/pdx213/local-install-bundle" \
  --hardlink
```

Use a clean checkout of the commit recorded by `out/build-report.json`, including
when the current branch has newer documentation. The userdata package must have
been assembled from that exact build. `--hardlink` avoids duplicate multi-GiB
images on the same filesystem; otherwise files are copied. Never change the
source images after preparing the bundle. Sony OEM must first pass
`tools/verify_sony_oem.py` with `--fastboot-output`; accepting equal decoded bytes
alone would overlook the bootloader's FILL-chunk limitation.

The current manual vendor input and Sony OEM keep this bundle local. Public CI
kernel/boot artifacts do not provide these inputs or qualify a complete stock-
baseline installation. See [installation qualification](INSTALLATION-QUALIFICATION.md)
and [vendor requirements](VENDOR.md).

## Local source-vendor installation candidate

`package_userdata.py` also accepts `--source-checkout` pointing to the clean
exact commit recorded by the selected CI build. This keeps build identity
checks intact when using a newer packaging utility. The assembly report records
the SHA256 of that utility and its vendor-input verifier separately.

To qualify a source-built vendor locally, provide `--vendor-build-report` and
its explicitly reviewed `--vendor-build-report-sha256` alongside `--vendor`.
The packager checks the image hash, manifest, Docker recipe, builder and full
project/patch inventory against the locked recipe. The report identifies patched
source commits and immutable container identity; it is not a reproducibility or
licensing attestation. The assembly report binds the vendor identity and report
pin to the resulting images. Without these explicit inputs the default remains
the checksum-locked vendor. This local mode does not enable public full-image CI
or imply hardware qualification or redistribution approval.
