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
