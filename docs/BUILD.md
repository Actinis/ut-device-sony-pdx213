# Noble source build

Use Linux x86_64 with GNU make, a C compiler, flex, bison, bc, OpenSSL/ELF
headers, Python 3, tar, unzip, readelf, kmod and qemu-aarch64. For full local image
assembly also install fakeroot, mksquashfs, mke2fs, img2simg and avbtool.

```sh
export UT_PORTS_DATA_DIR=/path/to/ut-ports-data
mkdir -p "$UT_PORTS_DATA_DIR"/{downloads,toolchains,builds/pdx213,releases/pdx213,evidence/pdx213,private/pdx213}
```

Use an SSD checkout and HDD data if desired. Supply all tool paths explicitly.
Obtain the NDK archive from `sources.lock.json`, verify its SHA256, and extract
it to `toolchains/`. Clone the kernel and mkbootimg at the full commits in the
lock. Initialize the kernel submodules with `git submodule update --init
--recursive`. Neither checkout may have local changes. Build output must be a
new directory and is never written into the source checkout.

```sh
python3 tools/build.py \
  --kernel-source /path/to/ut-kernel-sony-msm \
  --ndk "$UT_PORTS_DATA_DIR/toolchains/android-ndk-r23b" \
  --mkbootimg-source /path/to/mkbootimg \
  --build-id clean-noble-001 --jobs 4 --fetch-inputs
```

The build verifies the exact Git commits, tracked input hashes, Noble rootfs
and initrd checksums. It compiles Image.gz-dtb, DTBO, installs kernel modules, builds the Linux syscall helper
and Android compatibility library; stages ext4 tools from the locked rootfs;
creates the release boot image; and executes its BusyBox shell under QEMU.
`build-report.json` records inputs and output hashes. This is a real kernel/boot
build, not full userdata assembly or hardware qualification. AppArmor and PMF
fixes are in-tree; do not run an apply-backport script.

CI retains kernel/boot build results for 30 days as a GitHub Actions artifact,
including boot, DTBO, Image.gz-dtb, modules, helpers, build-report and input
identity. The tar archive preserves executable modes. These are experimental
build outputs, not an installation release; vendor/OEM and userdata are excluded.

## Local development userdata assembly

After resolving the manual vendor input, use its explicit file path:

```sh
fakeroot python3 tools/package_userdata.py --build-id clean-noble-001 \
  --vendor /path/to/reviewed-vendor.img \
  --mksquashfs /path/to/mksquashfs --mke2fs /path/to/mke2fs \
  --img2simg /path/to/img2simg --avbtool /path/to/avbtool
```

This freshly extracts the locked rootfs under fakeroot, applies the public
overlay, disables SSH, resets per-device state, runs the locale regression,
and assembles ordinary ext4 userdata. Explicit RAW sparse chunks avoid Sony's
observed large FILL write failure. OEM is excluded. A version-checked CamX guard
is applied in RAM at runtime; immutable Sony images are not rewritten.

The current scripts assemble local experimental images only. Do not regard a
build as installation, restoration or redistribution qualification. There is
no automatic release publication, tag creation, flashing or OTA.
