# Sony OEM input

Each user obtains **SW_binaries_for_Xperia_Android_11_4.19_v9a_lena.zip**
directly from [Sony](https://opendevices.sony.net/file/download/software-binaries-for-aosp-android-11-0-kernel-4-19-lena)
after reviewing and accepting the EULA presented there. OEM is excluded from
Git, CI and public image bundles. Do not substitute a different family/version.

```sh
python3 tools/verify_sony_oem.py \
  --archive /path/to/SW_binaries_for_Xperia_Android_11_4.19_v9a_lena.zip \
  --output /path/to/SW_binaries_for_Xperia_Android_11_4.19_v9a_lena.img
```

The verifier checks the archive SHA256, exact member name/size and extracted
image SHA256 against `sources.lock.json`. It does not download, accept licence
terms, modify the phone or flash anything. The output is the original Sony
Android sparse image. Fastboot accepts that image; do not pad or rewrite it to
match a partition-backup hash.

## Verified acquisition

An independently downloaded official archive passed ZIP integrity checking.
Its sparse image is 351,883,808 bytes; decoding it yields 838,860,800 bytes.
All 960 extracted entries match the qualified prototype's OEM: file hashes,
symlink targets, modes, UID/GID and extended attributes (including SELinux).
Full raw-image SHA256 differs, so byte-for-byte partition identity is not
claimed. Both official sparse and decoded hashes are recorded in the lock.
No independently downloaded OEM has been flashed in this qualification.

The final installation instructions must still qualify the exact stock
firmware baseline and target OEM partition/slot on XQ-BT52. Logical file
comparison does not establish safe installation or restoration.
