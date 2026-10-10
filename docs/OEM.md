# Sony OEM input

Each user obtains **SW_binaries_for_Xperia_Android_11_4.19_v9a_lena.zip**
directly from [Sony](https://opendevices.sony.net/file/download/software-binaries-for-aosp-android-11-0-kernel-4-19-lena)
after reviewing and accepting the EULA presented there. OEM is excluded from
Git, CI and public image bundles. Do not substitute a different family/version.

```sh
python3 tools/verify_sony_oem.py \
  --archive /path/to/SW_binaries_for_Xperia_Android_11_4.19_v9a_lena.zip \
  --output /path/to/SW_binaries_for_Xperia_Android_11_4.19_v9a_lena.img \
  --fastboot-output /path/to/oem-v9a-fastboot.img
```

The verifier checks the archive SHA256, exact member name/size and extracted
image SHA256 against `sources.lock.json`. It does not download, accept licence
terms, modify the phone or flash anything. The output is the original Sony
Android sparse image. The optional distinct fastboot output expands FILL chunks
to RAW to avoid the large FILL write failures observed with Sony fastboot. Both
images are checked against the locked decoded SHA256 and size. The derived
sparse file has its own reported SHA256; it is not the original Sony file.
Do not pad either image to match a partition-backup hash. This host conversion
does not establish successful flashing of the OEM image.

## Verified acquisition

An independently downloaded official archive passed ZIP integrity checking.
Its sparse image is 351,883,808 bytes; decoding it yields 838,860,800 bytes.
All 960 extracted entries match the qualified prototype's OEM: file hashes,
symlink targets, modes, UID/GID and extended attributes (including SELinux).
Full raw-image SHA256 differs, so byte-for-byte partition identity is not
claimed. Both official sparse and decoded hashes are recorded in the lock.
The FILL-to-RAW conversion was verified on the official image: decoded identity
remains unchanged. The derived sparse image is 838,861,272 bytes with SHA256
`decb705b78c0ec68d07f46e0e118f48f69edb11693bf312396ecd604c2d42dc5`.
The independently downloaded v9a OEM was flashed to oem_a on the XQ-BT52
qualification device using RAW sparse chunks and a 128-MiB transfer limit. Its
838,860,800 decoded bytes were read back before first boot and matched the lock.
The complete local candidate reached the setup wizard and ran the stock Camera
video/photo/front-camera scenario. This test retained the existing firmware
baseline; it does not qualify installation after complete stock restoration.

The final installation instructions must still qualify the exact stock
firmware baseline and target OEM partition/slot on XQ-BT52. Logical file
comparison does not establish safe installation or restoration.
