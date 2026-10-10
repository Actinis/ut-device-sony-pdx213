#!/usr/bin/env python3
"""Prepare a local terminal-flashing candidate; never flash, download or publish."""
import argparse
import struct
import json
import os
from pathlib import Path
import re
import shutil
from build_manifest import build_identity, verify_build, sha
from sources_lock import validate
from verify_sony_oem import logical_identity


def require_file(path):
    if path.is_symlink() or not path.is_file() or not path.stat().st_size:
        raise ValueError('Expected a nonempty regular input: '+str(path))
    return path


def require_raw_sparse(path):
    # logical_identity validates all lengths and payloads first. Reject FILL even
    # when equivalent decoded bytes match: Sony flashing has hung on large FILL.
    logical_identity(path)
    with path.open('rb') as stream:
        header=struct.unpack('<I4H4I',stream.read(28))
        for _ in range(header[7]):
            kind,reserved,blocks,size=struct.unpack('<HHII',stream.read(12))
            if kind == 0xcac2:
                raise ValueError('Sony fastboot input contains FILL; convert to RAW first')
            stream.seek(size-12,1)
    return path


def candidate(build, repository, oem):
    lock_path=require_file(repository/'sources.lock.json')
    lock=validate(json.loads(lock_path.read_text()),repository)['sources']
    verify_build(build,build_identity(repository,build.name,lock))
    package=build/'userdata-package'
    assembly=json.loads(require_file(package/'assembly-report.json').read_text())
    if (assembly.get('build_report_sha256') != sha(build/'out/build-report.json')
            or assembly.get('input_identity_sha256') != sha(build/'input-identity.json')):
        raise ValueError('Userdata was assembled from another build')
    expected={'userdata.img','vbmeta.img'}
    if set(assembly.get('images',{})) != expected:
        raise ValueError('Incomplete or unexpected assembled image inventory')
    images={name:require_file(package/name) for name in expected}
    for name,path in images.items():
        if sha(path) != assembly['images'][name]:
            raise ValueError('Assembled image checksum mismatch: '+name)
    require_raw_sparse(images['userdata.img'])
    images.update({name:require_file(build/'out'/name) for name in ['boot.img','dtbo.img']})
    oem=require_raw_sparse(require_file(oem))
    if logical_identity(oem) != {'sha256':lock['sony_oem']['decoded_sha256'],
                                'bytes':lock['sony_oem']['decoded_bytes']}:
        raise ValueError('OEM decoded bytes do not match the locked Sony input')
    images['oem.img']=oem
    report=json.loads((build/'out/build-report.json').read_text())
    return images,{'schema_version':1,'device':'XQ-BT52','slot':'a',
        'ut_series':'24.04','device_commit':report['device_commit'],
        'kernel_commit':lock['kernel']['commit'],'build_id':build.name,
        'lock_sha256':sha(lock_path),'build_report_sha256':sha(build/'out/build-report.json'),
        'assembly_report_sha256':sha(package/'assembly-report.json'),
        'status':'experimental local installation candidate; clean-install qualification pending',
        'redistribution':'Not approved: vendor and user-obtained Sony OEM remain local',
        'images':{name:{'sha256':sha(path),'bytes':path.stat().st_size} for name,path in sorted(images.items())}}


def stage(images,manifest,destination,hardlink=False):
    destination.mkdir(mode=0o700,exist_ok=False)
    for name,path in images.items():
        if hardlink:os.link(path,destination/name)
        else:shutil.copyfile(path,destination/name)
    (destination/'install-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    files=list(images)+['install-manifest.json']
    (destination/'SHA256SUMS').write_text(''.join(sha(destination/name)+'  '+name+'\n' for name in sorted(files)))
    (destination/'FLASHING.md').write_text("""# XQ-BT52 local installation candidate

Experimental Ubuntu Touch 24.04, unlocked XQ-BT52, slot A only. Erases all userdata.
The Android 11 firmware/bootloader baseline must already be present. Do not change
GPT, TA, persist, modem/DSP/bootloader or relock the bootloader. This local bundle
contains owner-obtained OEM/vendor inputs and must not be uploaded or redistributed.
No OTA or universal Installer. A stock-baseline restoration test remains required.

From this directory, verify checksums before entering fastboot:

```sh
sha256sum -c SHA256SUMS
SERIAL='replace-with-your-fastboot-serial'
fastboot -s "$SERIAL" getvar product
fastboot -s "$SERIAL" getvar current-slot
fastboot -s "$SERIAL" getvar unlocked
```

Stop unless product is XQ-BT52, current-slot is a, and unlocked is yes.
Keep a verified recovery/stock restoration set before proceeding. Use current
Android platform-tools. The following commands are destructive to userdata:

```sh
fastboot -s "$SERIAL" -S 128M flash oem_a oem.img
fastboot -s "$SERIAL" erase userdata
fastboot -s "$SERIAL" -S 128M flash userdata userdata.img
fastboot -s "$SERIAL" flash dtbo_a dtbo.img
fastboot -s "$SERIAL" flash vbmeta_a vbmeta.img
fastboot -s "$SERIAL" flash vbmeta_system_a vbmeta.img
fastboot -s "$SERIAL" flash boot_a boot.img
fastboot -s "$SERIAL" reboot
```

Boot is written last. Do not use `fastboot -w` after installing populated userdata.
First boot expands the seed filesystem to the device's actual userdata partition.
Complete the setup wizard. SSH is disabled and private keys are not included.
""")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-checkout',type=Path,required=True,
                        help='Clean checkout of the exact device commit recorded by the build')
    parser.add_argument('--build-id',required=True)
    parser.add_argument('--oem-fastboot-image',type=Path,required=True,
                        help='Owner-obtained OEM processed by verify_sony_oem.py')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--hardlink',action='store_true',help='Avoid copying large local images on the same filesystem')
    args=parser.parse_args()
    if not re.fullmatch('[A-Za-z0-9][A-Za-z0-9._-]*',args.build_id):parser.error('Safe build ID required')
    if not os.environ.get('UT_PORTS_DATA_DIR'):parser.error('UT_PORTS_DATA_DIR required')
    build=Path(os.environ['UT_PORTS_DATA_DIR']).resolve()/'builds/pdx213'/args.build_id
    try:
        images,manifest=candidate(build,args.source_checkout,args.oem_fastboot_image)
        stage(images,manifest,args.output,args.hardlink)
    except (ValueError,OSError) as error:parser.error(str(error))
    print('Local candidate prepared; no flash or publication performed: '+str(args.output))

if __name__=='__main__':main()
