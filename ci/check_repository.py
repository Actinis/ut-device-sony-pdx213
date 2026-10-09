#!/usr/bin/env python3
"""Validate port metadata without downloading dependencies or building images."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
for path in sorted(root.rglob("*.json")):
    if ".git" not in path.parts:
        json.loads(path.read_text())
lock = root / "sources.lock.json"
if lock.exists():
    data = json.loads(lock.read_text())
    assert data["schema_version"] == 1
    assert data["ubuntu_touch"] == "24.04"
    assert data["device"] == "sony-pdx213"
    assert data["status"] in ("unpopulated", "locked")
    sources = data["sources"]
    assert isinstance(sources, dict)
    if data["status"] == "unpopulated":
        assert sources == {}, "An unpopulated lock must not appear partially usable"
    else:
        assert set(sources) == {"kernel", "rootfs", "halium_gsi", "toolchain"}
        for name, source in sources.items():
            assert isinstance(source, dict)
            assert isinstance(source.get("url"), str) and source["url"].startswith("https://")
            if name == "kernel":
                assert re.fullmatch(r"[0-9a-f]{40}", source.get("commit", ""))
            else:
                assert isinstance(source.get("version"), str) and source["version"].strip()
                assert re.fullmatch(r"[0-9a-f]{64}", source.get("sha256", ""))
print("Repository metadata valid; no kernel or image build was performed.")
