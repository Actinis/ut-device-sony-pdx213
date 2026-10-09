#!/usr/bin/env python3
"""Reserve an exact development source ref while its workflow commit is current."""
import json
import os
from pathlib import Path
import re
import subprocess
from publish_ci_release import REPOSITORY, api, gh
from sources_lock import validate


def reserve(tag, commit):
    result = subprocess.run(['gh', 'api', f'repos/{REPOSITORY}/git/ref/tags/{tag}'], capture_output=True, text=True)
    if result.returncode != 0:
        gh('api', '--method', 'POST', f'repos/{REPOSITORY}/git/refs', '-f', 'ref=refs/tags/' + tag, '-f', 'sha=' + commit)
    ref = api(f'repos/{REPOSITORY}/git/ref/tags/{tag}')['object']
    while ref['type'] == 'tag':
        ref = api(f"repos/{REPOSITORY}/git/tags/{ref['sha']}")['object']
    if ref['type'] != 'commit' or ref['sha'] != commit:
        raise ValueError('Reserved tag does not identify the exact source commit')


def main():
    if os.environ['GITHUB_REPOSITORY'] != REPOSITORY:
        raise ValueError('Unexpected repository')
    source_ref = os.environ['GITHUB_REF']
    commit = os.environ['GITHUB_SHA']
    if source_ref.startswith('refs/tags/'):
        tag = source_ref.removeprefix('refs/tags/')
        if not re.fullmatch(r'pdx213-noble-port-v[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.]+)?', tag):
            raise ValueError('Unexpected port version tag')
    elif source_ref == 'refs/heads/main':
        lock = json.loads(Path('sources.lock.json').read_text())
        validate(lock)
        series = re.search(r'\b(24\.04-[0-9]+\.x)\b', lock['sources']['rootfs']['version'])
        if not series:
            raise ValueError('Missing Ubuntu Touch rootfs series')
        tag = f"pdx213-ut{series.group(1)}-daily-{os.environ['GITHUB_RUN_ID']}-{os.environ['GITHUB_RUN_ATTEMPT']}-{commit[:7]}"
    else:
        raise ValueError('Release builds require main or a port version tag')
    reserve(tag, commit)
    print('Reserved source tag: ' + tag)


if __name__ == '__main__':
    main()
