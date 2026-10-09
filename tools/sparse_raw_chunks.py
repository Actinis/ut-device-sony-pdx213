#!/usr/bin/env python3
"""Expand Android sparse FILL chunks to RAW for Sony bootloader compatibility."""
import argparse
import struct
from pathlib import Path


def convert(source, destination):
    if source.resolve() == destination.resolve():
        raise ValueError('Input and output must differ')
    with source.open('rb') as inp, destination.open('xb') as out:
        header = inp.read(28)
        if len(header) != 28:
            raise ValueError('Truncated header')
        magic, major, minor, hs, cs, blocksize, blocks, count, crc = struct.unpack('<I4H4I', header)
        if magic != 0xed26ff3a or major != 1 or hs != 28 or cs != 12 or blocksize % 4 or not blocksize:
            raise ValueError('Unsupported sparse header')
        out.write(header)
        logical = 0
        for _ in range(count):
            chunk = inp.read(cs)
            if len(chunk) != cs:
                raise ValueError('Truncated chunk')
            kind, reserved, length, size = struct.unpack('<HHII', chunk)
            expected = {0xcac1: length * blocksize, 0xcac2: 4, 0xcac3: 0, 0xcac4: 4}.get(kind)
            if expected is None or size != cs + expected:
                raise ValueError('Invalid chunk size')
            if kind == 0xcac4:
                if length:
                    raise ValueError('Invalid CRC chunk')
            else:
                logical += length
            if kind == 0xcac2:
                pattern = inp.read(4)
                if len(pattern) != 4:
                    raise ValueError('Truncated fill')
                remaining = length * blocksize
                out.write(struct.pack('<HHII', 0xcac1, reserved, length, remaining + cs))
                batch = pattern * (1024 * 1024 // 4)
                while remaining:
                    data = batch[:min(remaining, len(batch))]
                    out.write(data)
                    remaining -= len(data)
            else:
                out.write(chunk)
                remaining = expected
                while remaining:
                    data = inp.read(min(remaining, 1024 * 1024))
                    if not data:
                        raise ValueError('Truncated payload')
                    out.write(data)
                    remaining -= len(data)
        if logical != blocks or inp.read(1):
            raise ValueError('Invalid total sparse length')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    convert(args.source, args.destination)
