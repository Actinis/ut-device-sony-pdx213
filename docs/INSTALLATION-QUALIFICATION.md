# Installation and restoration qualification

No generalized installation procedure has been approved yet. The current development phone uses a device-specific legacy storage layout.

Before a public installable release, record:

- Exact supported model, variant, bootloader state and firmware prerequisites.
- Required partitions, slot behavior, image size limits and storage assumptions.
- Data-loss boundaries, backup requirements and recovery entry method.
- Installation from a documented baseline, first boot and repeated cold boots.
- Hardware results using HARDWARE.md, including suspend and battery behavior.
- Restoration to the baseline OS and recovery from interrupted installation.
- Checksums, source commits, build run, test date and sanitized evidence.

Provide reviewed commands only after validating them on the named variant. Do not generalize measured partition mappings from one phone or claim untested variants. Build success does not establish installation or restoration safety.
