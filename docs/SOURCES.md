# Source lock contract

`sources.lock.json` is preparation metadata, not a usable build recipe until status is `locked`.

Schema version 1 requires `device: sony-pdx213`, `ubuntu_touch: 24.04` and status `unpopulated` or `locked`. Unpopulated sources must be an empty object.

A locked file requires exactly these source entries:

| Entry | Required fields |
| --- | --- |
| kernel | HTTPS Git URL, full 40-character commit |
| rootfs | HTTPS artifact URL, exact version/build, SHA256 |
| halium_gsi | HTTPS artifact URL, exact version/build, SHA256 |
| toolchain | HTTPS artifact URL, exact version, SHA256 |

The build must reject unpopulated locks, fetch the exact kernel commit, and verify artifact hashes before use. No build implementation exists yet. Additional inputs such as boot metadata, initrd or auxiliary libraries must be inventoried during source import; extend the contract and validator before declaring the build reproducible.

Device adaptation commit belongs in the release manifest. A lock file cannot contain the hash of its own enclosing commit.
