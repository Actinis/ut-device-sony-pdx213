#!/usr/bin/env python3
"""Validate repository metadata and all Noble source pins; never build images."""
import json
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from sources_lock import validate
for path in root.rglob('*.json'):
    if '.git' not in path.parts: json.loads(path.read_text())
validate(json.loads((root/'sources.lock.json').read_text()),root)
print('Noble source lock valid; no image or hardware check performed')
