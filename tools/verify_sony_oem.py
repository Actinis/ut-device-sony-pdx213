#!/usr/bin/env python3
"""Verify and extract a user-obtained Sony OEM archive; no download or flash."""
import argparse
import json
from pathlib import Path
import shutil
import zipfile
from build_manifest import sha
from sources_lock import validate
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    entry = validate(json.loads((ROOT/'sources.lock.json').read_text()), ROOT)['sources']['sony_oem']
    extract(args.archive, args.output, entry)
    print('Official Sony sparse OEM verified; not flashed or bundled')


if __name__ == '__main__':
    main()
