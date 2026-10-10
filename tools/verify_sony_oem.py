#!/usr/bin/env python3
"""Verify and extract a user-obtained Sony OEM archive; no download or flash."""
import argparse
import json
import hashlib
import struct
from pathlib import Path
import shutil
import zipfile
from build_manifest import sha
from sources_lock import validate
from sparse_raw_chunks import convert
ROOT = Path(__file__).resolve().parents[1]


def extract(archive, output, entry):
    if sha(archive) != entry['archive']['sha256']:
        raise ValueError('Sony archive checksum mismatch')
    if output.exists() or output.is_symlink():
        raise ValueError('Output must not already exist')
    with zipfile.ZipFile(archive) as stream:
        matches = [item for item in stream.infolist() if item.filename == entry['filename']]
        if len(matches) != 1 or matches[0].file_size != entry['bytes']:
            raise ValueError('Unexpected Sony OEM archive contents')
        with stream.open(matches[0]) as source, output.open('xb') as target:
            shutil.copyfileobj(source, target)
    if sha(output) != entry['sha256']:
        output.unlink()
        raise ValueError('Extracted Sony sparse image checksum mismatch')



def logical_identity(path):
    """Hash decoded sparse bytes, treating DONT_CARE as zero like simg2img."""
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        header = stream.read(28)
        if len(header) != 28:
            raise ValueError('Truncated sparse header')
        magic, major, minor, hs, cs, blocksize, blocks, count, crc = struct.unpack('<I4H4I', header)
        if magic != 0xed26ff3a or major != 1 or hs != 28 or cs != 12 or not blocksize or blocksize % 4:
            raise ValueError('Unsupported sparse header')
        logical = 0
        for _ in range(count):
            chunk = stream.read(12)
            if len(chunk) != 12:
                raise ValueError('Truncated sparse chunk')
            kind, reserved, length, size = struct.unpack('<HHII', chunk)
            expected = {0xcac1: length * blocksize, 0xcac2: 4, 0xcac3: 0, 0xcac4: 4}.get(kind)
            if expected is None or size != 12 + expected or (kind == 0xcac4 and length):
                raise ValueError('Invalid sparse chunk')
            if kind == 0xcac4:
                if len(stream.read(4)) != 4:
                    raise ValueError('Truncated sparse CRC')
                continue
            remaining = length * blocksize
            logical += length
            if kind == 0xcac2:
                pattern = stream.read(4)
                if len(pattern) != 4:
                    raise ValueError('Truncated sparse fill')
                batch = pattern * (1024 * 1024 // 4)
            elif kind == 0xcac3:
                batch = bytes(1024 * 1024)
            while remaining:
                n = min(remaining, 1024 * 1024)
                data = stream.read(n) if kind == 0xcac1 else batch[:n]
                if len(data) != n:
                    raise ValueError('Truncated sparse payload')
                digest.update(data)
                remaining -= n
        if logical != blocks or stream.read(1):
            raise ValueError('Invalid total sparse length')
    return {'sha256': digest.hexdigest(), 'bytes': blocks * blocksize}


def prepare_fastboot(source, output, entry):
    if sha(source) != entry['sha256'] or source.stat().st_size != entry['bytes']:
        raise ValueError('Input is not the locked official sparse image')
    expected = {'sha256': entry['decoded_sha256'], 'bytes': entry['decoded_bytes']}
    if logical_identity(source) != expected:
        raise ValueError('Official OEM decoded identity mismatch')
    if output.exists() or output.is_symlink() or source.resolve() == output.resolve():
        raise ValueError('Fastboot output must be a new distinct file')
    try:
        convert(source, output)
        if logical_identity(output) != expected:
            raise ValueError('Converted OEM decoded identity mismatch')
    except Exception:
        output.unlink(missing_ok=True)
        raise
    return {'sha256': sha(output), 'bytes': output.stat().st_size, 'decoded': expected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--fastboot-output', type=Path, help='Optional distinct output with FILL expanded to RAW')
    args = parser.parse_args()
    entry = validate(json.loads((ROOT/'sources.lock.json').read_text()), ROOT)['sources']['sony_oem']
    extract(args.archive, args.output, entry)
    if args.fastboot_output:
        print(json.dumps(prepare_fastboot(args.output, args.fastboot_output, entry), sort_keys=True))
    print('Official Sony sparse OEM verified; not flashed or bundled')


if __name__ == '__main__':
    main()
