# NFC qualification sources

Experimental source patches for the XQ-BT52 NFC stack. They are not connected
to the production image build yet. Existing images do not include them
automatically.

The installed qualification stack reads and writes UTF-8 Text NDEF on a
preformatted MIFARE Classic 1K card through org.neard.Tag.Write. A real-card
write, independent reread, restoration and byte-for-byte original NDEF
comparison passed. Reader startup after reboot and three adapter power cycles
are qualified. Writer startup after reboot has not been tested.

Twenty-two ARM64 reader/writer tests pass, covering the NXP MAD CRC reference,
authentication failure, corrupt/access-denied sector permissions, short reads,
negative write acknowledgements, readback mismatch, cancellation/removal,
bounds, concurrent requests, crossing sector boundaries, preservation of
following TLVs and growing a message into unused bytes after a Terminator. These tests use synthetic card data.

## Supported write operation

Only an existing Classic 1K public NDEF mapping with writable data blocks is
supported. The writer authenticates using the standard public NDEF Key A,
validates complementary access bits and GPB, preflights all affected blocks,
invalidates and checks the TLV length, writes the body, commits the first block,
and verifies the complete result by reading it back. It never changes the MAD,
manufacturer blocks, keys or sector trailers. Growth into following nonempty
TLVs is rejected. Formatting, private Key B authentication, URI writing, other
tag types, card emulation and payments are not qualified.

Keep the card stationary until Write completes. An interrupted write may leave
an empty or incomplete message; save the original NDEF before writing. This is
not a transactional storage protocol. A failed operation must not be reported
as a successful write. Each successful write deactivates the current tag so
rediscovery refreshes exported records.

On the phone, obtain the currently detected tag path:

```sh
busctl --system tree org.neard
```

For example, if that path is `/nfc0/tag0`:

```sh
busctl --system call org.neard /nfc0/tag0 org.neard.Tag Write 'a{sv}' 4 \
  Type s Text Representation s 'Ubuntu Touch NFC test' \
  Language s en Encoding s UTF-8
```

The tag path changes on rediscovery. Use the actual current path. This writes
through D-Bus; a graphical tag-writing application is not supplied here.

## Build integration remaining

The experimental input manifest pins upstream commits and patch SHA256 hashes.
Copyright and licensing notices remain in the patches. Do not distribute
libraries extracted from a personal phone, card identifiers, contents or raw
private logs. Only synthetic fixtures belong in the public source tree.

Before using these patches in normal image builds: pin Noble gdbus-codegen and
replace compatibility flags; extract linker inputs from locked Android/Ubuntu
images; update NCI2 fixtures; cover binder initialization/cancellation; preserve
distribution daemon integration; remove diagnostic logs; add mandatory NFC
outputs and packaging; enforce relinking when static core libraries change.
The experimental scripts still use local tool/header paths and must not ship.

## Qualified runtime layout

`runtime/27-utxperia-nfc` is the qualified LXC pre-start hook, installed on the
phone under `/var/lib/lxc/android/pre-start.d/`. It copies the replacement HAL
into the assembled vendor overlay; it does not flash the vendor partition.
`runtime/utxperia-nfc.conf` is the daemon override installed under
`/etc/systemd/system/nfcd.service.d/`. These files are examples of the qualified
runtime setup and are not automatically installed by the image builder.

The runtime directory `/usr/local/lib/utxperia/nfc/` must contain `nfcd`,
`nfc_nci_nxp.so`, `binder.so`, `libncicore.so.1`, `libnciplugin.so.1`, and a
`plugins/` directory. The latter links `binder.so` to the adapted plugin and
links the other plugins to their installed `/usr/lib/nfcd/plugins/` counterparts.
Deploy all mutually dependent binaries together. Do not copy the hook into an
image without providing its required HAL artifact, or enable the service override
without the complete daemon/plugin/library set.
