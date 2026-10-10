build.py builds kernel/boot from sources.lock.json; package_userdata.py performs separate fakeroot assembly with an explicit reviewed vendor input. Paths use UT_PORTS_DATA_DIR and explicit tool arguments. release_metadata.py prepares metadata only; no tool in this repository automatically flashes or publishes.

The full build also compiles the camera microphone-startup repair with the pinned
ARM64 Noble Qt generator. Pass `--qemu-aarch64` explicitly when its executable is
not on PATH. Camera binaries, cancellation results, component identity and the
upstream LGPL licence are required artifacts; userdata packaging rejects missing
or stale camera outputs. See `device/camera/README.md`.
