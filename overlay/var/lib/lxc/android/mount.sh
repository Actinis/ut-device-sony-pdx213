#!/bin/sh
set -eu
for spec in 'null 1 3 666' 'kmsg 1 11 600' 'random 1 8 666' 'urandom 1 9 666'; do
    set -- $spec
    [ -c "${LXC_ROOTFS_MOUNT}/dev/$1" ] || mknod -m "$4" "${LXC_ROOTFS_MOUNT}/dev/$1" c "$2" "$3"
done
chmod 440 "${LXC_ROOTFS_MOUNT}/proc/cmdline"
if [ -w "$LXC_ROOTFS_MOUNT" ]; then
    # -T avoids following an existing socket symlink into the shared /dev/socket.
    ln -sfnT /dev/socket "${LXC_ROOTFS_MOUNT}/socket"
fi
