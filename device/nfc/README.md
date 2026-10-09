# NFC qualification sources

The Noble image build compiles the SN100 HAL, its public HIDL interface library,
NCI core/plugin, binder plugin and daemon from pinned public sources. The rootfs
packager installs these as one set. Build integration does not itself qualify
the resulting images on hardware.

## Qualification on XQ-BT52

| Operation | Evidence | Limit |
| --- | --- | --- |
| Classic 1K NDEF Text reading | Real card read and rediscovery; reader worked after reboot | One public NDEF-formatted card |
| Classic 1K UTF-8 Text writing | Real write, independent reread, original restoration and byte-for-byte comparison passed | Existing writable public NDEF mapping only; writer after reboot untested |
| NFC off/on | Three power cycles and reread passed | Screen unlocked during tests |
| ISO-DEP discovery/exchange | Residence-permit card remained present for 15 seconds; bank card passed 104 consecutive presence checks without interface errors in a repeated test | No protected applications read; earlier transient RF timeouts have no established cause |
| NTAG/Type 2, Type 3, Type 4 NDEF, ISO15693 | No physical qualification | ISO-DEP detection is not Type 4 NDEF qualification |
| Formatting, other write record types, private keys, card emulation, payments | Not qualified | No payment application is provided |
| Suspend/resume, screen-lock behavior, long-term reliability | Not qualified | Short foreground tests do not establish these |

Twenty-two ARM64 reader/writer tests passed with synthetic card data: NXP MAD
CRC reference, authentication failure, corrupt/access-denied sector permissions,
short reads, negative acknowledgements, readback mismatch, cancellation/removal,
bounds, concurrent requests, crossing sector boundaries, preservation of following
TLVs and growth into unused bytes after a Terminator. These tests do not replace
physical qualification. Binder initialization/cancellation and the complete NCI2
state-machine regression suite remain qualification gaps.

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

## Reproducible build inputs and runtime

`inputs.json` pins eight upstream Git commits, five patch hashes and ten Noble
or UBports development packages. `ORIGINS.json` records the origins of tracked
public HIDL/VNDK headers and generated interface sources. Common headers come
from the locked GNSS bundle. `sources.lock.json` schema 4 hashes the complete
NFC source inventory and declares these dependencies. Licenses and copyright
notices are retained. No linker library is obtained from a connected phone.

`tools/build_nfc.py` uses the explicitly supplied NDK r23b, locked GSI and Noble
rootfs, separate work/output directories, and downloads cache. Portable Python
`gdbus-codegen` comes from the pinned Noble package. Every upstream checkout is
fresh and patches are checked before application. The report binds input and
lock hashes, runtime linker-input identities and all six output hashes. Missing,
linked or changed outputs and mismatched resume inputs are rejected.

The normal builder requires the daemon, binder plugin, NCI libraries, SN100 HAL,
public NXP eSE HIDL interface library and NFC report. The interface library is
transport glue; it does not implement or qualify secure-element functions.
Packaging validates the enclosing completed build report before rootfs changes.

The daemon override under `overlay/etc/systemd/system/nfcd.service.d/` loads the
complete stack from `/usr/local/lib/utxperia/nfc/`. The daemon honors the distribution service
setting `NFCD_NO_STOP_POLL_LOOP=1` so client cleanup does not disable discovery.
Its plugin directory links the
adapted binder plugin and the other distribution plugins. The LXC pre-start
hook copies the HAL and its interface library into the assembled vendor overlay;
it does not flash the vendor partition. Deploy all mutually dependent binaries
together. `runtime/` contains matching examples of these integration files.

Card identifiers, card contents, backups and raw private logs are excluded from
public sources. Only synthetic fixtures are published. Build success, phone
qualification and installation/redistribution qualification are separate claims.
