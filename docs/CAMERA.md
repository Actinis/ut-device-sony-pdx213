# Sony camera HAL compatibility

The XQ-BT52 adaptation uses Sony Android 11 v9a Camera1 HAL in its stock two-camera
mode. Extra rear lenses are disabled because their mode is not reliable.
ODM and calibration stay read-only.

The version-checked patch_camx_node_destroy.py protects six mutex Lock/Unlock
calls in CamX Node::Destroy when optional cleanup mutexes are null. It retains
the original call on non-null pointers and rejects different hashes, ELF layouts,
instructions or unavailable executable alignment padding. This is a scoped
binary compatibility repair, not a complete CamX audit or source-level vendor fix.
Original library SHA256:
6556265bdc97837b7c795ad5f69410da6bd7e564067f9abc0f8e30242a0feaf7.
Patched library SHA256:
baed8c7fbfb13b3a1fa09ab44d07282ad3594c39238f5ac7674862e6085ecd63.

utxperia-camera-compat runs before LXC Android, creates a corrected copy in RAM,
and uses a private read-only bind for that library only. Unsupported library
versions remain unchanged with a warning. No Sony binary is shipped in Git.
Removing the scoped lxc-android-config service drop-in disables this integration.

On the prototype, main-camera H.264/AAC clips of 69.781, 89.728 and 11.840 seconds
and a front-camera clip of 69.654 seconds passed full strict decoding. Stops were
followed by main/front JPEG capture and switching with the provider remaining
alive. A 78.208-second recording through the normal camera UI, stop, JPEG and
screen-off/resume also passed. Generated QEMU fixtures exercised all six guard
sites, both pointer cases, flags, stack and callee-saved registers.
Longer sessions, other codecs and extra rear lenses remain unqualified.
Raw private videos and logs are retained outside the public repository.
