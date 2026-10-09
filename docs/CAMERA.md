# Sony CamX recording-stop repair

This adaptation targets the owner's XQ-BT52 with the Sony Android 11 v9a
camera HAL. The original ODM partition and calibration remain read-only.
The boot image remains v10; the repair is applied by the rootfs overlay.

## Cause and scope

Stopping native Camera1 video reconfigures the preview/still streams. Sony
CamX tears down an MFSR processing node. `Node::Destroy` assumes its optional
cleanup mutexes exist, although `Node::Initialize` can leave them null after
partial initialization. The observed abort reaches `pthread_mutex_lock(NULL)`
through the `BufferReleaseLock` field. Guarding only that pair exposed another
null call through `Fence_Create_Release`, confirming a second instance of the
same cleanup defect.

The exact original library SHA-256 is
`6556265bdc97837b7c795ad5f69410da6bd7e564067f9abc0f8e30242a0feaf7`;
its ELF Build ID is `d54d738bb6352882977367309c24c611`.
Focused native inspection covered destruction and initialization of these
mutexes. This is not a complete audit of Sony CamX or a source-level vendor fix.

`patch_camx_node_destroy.py` guards six direct Lock/Unlock calls within
`Node::Destroy` (0x8cb100), using the original functions for every non-null
pointer. The fields are 0x6bf0 and 0x6bf8; call sites are 0x8cb2d4, 0x8cb844,
0x8cb84c, 0x8cb94c, 0x8cbd60 and 0x8cc080. Two 12-byte AArch64 stubs occupy
verified zero executable-segment alignment padding at 0x9bcef0. Each stub
returns on a null pointer and otherwise tail-calls the original method.
Other call sites, cleanup work, mutex implementations and CFI remain unchanged.

The patcher rejects other hashes, unexpected ELF segment metadata, instruction
mismatches and unavailable padding. It writes a separate output file.
The expected patched SHA-256 is
`baed8c7fbfb13b3a1fa09ab44d07282ad3594c39238f5ac7674862e6085ecd63`.

## Boot integration and rollback

`utxperia-camera-compat` runs before `lxc-android-config`. It preserves a
private read-only bind of the original library at `/run/utxperia/camera.qcom-original.so`,
generates the corrected library in RAM and overlays only the HAL library with
a read-only bind mount. A different future Sony HAL is left unchanged with a
warning; Android startup is not blocked by an unsupported version.

Remove `/etc/systemd/system/lxc-android-config.service.d/utxperia-camera-compat.conf`
and reboot to return to the original camera HAL. No vendor partition flashing,
calibration changes or relaxed AppArmor policy are involved.

## Validation

All six guarded call sites passed generated AArch64 execution tests under QEMU:
null pointers skip the original method; non-null pointers call it exactly once;
return behavior, stack and callee-saved registers are preserved. The null path
also preserves condition flags. A wrong input hash was rejected.

Before this repair, a 68.544-second 1920x1080 recording decoded correctly but
crashed the HAL on stop. Disabling MFNR, selected advanced feature bits or
offline noise processing did not repair the crash. Disabling all advanced
features prevented stream configuration. Stock Sony settings were restored.

Device regression and cold-boot results are recorded in `HARDWARE.md` and
`evidence/camera-guard-suite.json`. Large clips and full logs remain privately
under `/hdd1/ut-xperia/evidence`; Sony binaries are not shipped in the source bundle.

The qualified sequence includes main 69.781/89.728/11.840 s and front 69.654 s
clips followed by main/front JPEG captures. Provider PID remained 1349 throughout.
After installing the boot helper and rebooting, original and patched hashes were
verified independently. The original camera app QML then recorded 78.208 s using
normal touch controls; stop, JPEG capture and screen-off/resume succeeded with
provider PID 1369 unchanged. All five videos passed full strict decoding and no
HAL crash was logged. Sessions longer than these remain unqualified.
