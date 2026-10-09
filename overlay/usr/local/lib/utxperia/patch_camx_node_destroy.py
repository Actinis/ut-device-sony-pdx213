#!/usr/bin/env python3
"""Guard optional cleanup mutexes in this Xperia's Sony CamX destructor.

Only this exact ELF is supported. The original file is never modified. Six
direct calls in Node::Destroy go through null guards; non-null mutexes still
use the original Lock/Unlock functions. Other callers and cleanup stay intact.
"""
import argparse
import hashlib
from pathlib import Path
import struct

ORIGINAL_SHA256 = "6556265bdc97837b7c795ad5f69410da6bd7e564067f9abc0f8e30242a0feaf7"
LOCK, UNLOCK = 0x73498C, 0x734C70
STUB = 0x9BCEF0
CALLS = ((0x8CB2D4, LOCK, 0x6BF8), (0x8CB844, UNLOCK, 0x6BF8),
         (0x8CB84C, LOCK, 0x6BF0), (0x8CB94C, UNLOCK, 0x6BF0),
         (0x8CBD60, LOCK, 0x6BF8), (0x8CC080, UNLOCK, 0x6BF8))


def branch(source, target, link=False):
    distance = target - source
    if distance % 4 or not -(1 << 27) <= distance < (1 << 27):
        raise ValueError("AArch64 branch out of range")
    return struct.pack("<I", (0x94000000 if link else 0x14000000) |
                       ((distance // 4) & 0x3FFFFFF))


def patch(original):
    if hashlib.sha256(original).hexdigest() != ORIGINAL_SHA256:
        raise ValueError("Unsupported Sony camera HAL SHA-256")
    image = bytearray(original)
    # PT_LOAD containing executable code; grow only into zero alignment padding.
    header = 64 + 2 * 56
    expected = (1, 5, 0x257000, 0x257000, 0x257000,
                0x765EF0, 0x765EF0, 0x1000)
    if struct.unpack_from("<IIQQQQQQ", image, header) != expected:
        raise ValueError("Unexpected executable segment")
    if any(image[STUB:STUB + 24]) or STUB + 24 >= 0x9BD000:
        raise ValueError("Executable padding is unavailable")
    for call, target, field in CALLS:
        stub = STUB if target == LOCK else STUB + 12
        load = struct.pack("<I", 0xF9400000 | ((field // 8) << 10) | (19 << 5))
        if image[call - 4:call] != load:
            raise ValueError("Cleanup mutex load mismatch")
        if image[call:call + 4] != branch(call, target, True):
            raise ValueError("Original mutex call mismatch")
        image[call:call + 4] = branch(call, stub, True)
        # cbz x0, return; b original_method; return: ret
        # Tail calls preserve the original return address and stack frame.
        image[stub:stub + 12] = (bytes.fromhex("400000b4") +
                                branch(stub + 4, target) +
                                bytes.fromhex("c0035fd6"))
    new_size = STUB + 24 - expected[2]
    struct.pack_into("<QQ", image, header + 32, new_size, new_size)
    return bytes(image)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.original.resolve() == args.output.resolve():
        parser.error("Output must differ from the original")
    result = patch(args.original.read_bytes())
    args.output.write_bytes(result)
    print(hashlib.sha256(result).hexdigest())


if __name__ == "__main__":
    main()
