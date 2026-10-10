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
    return images,{'schema_version':1,'bundle_tool_sha256':sha(Path(__file__)),'device':'XQ-BT52','slot':'a',
        'ut_series':'24.04','device_commit':report['device_commit'],
        'kernel_commit':lock['kernel']['commit'],'build_id':build.name,
        'lock_sha256':sha(lock_path),'build_report_sha256':sha(build/'out/build-report.json'),
        'assembly_report_sha256':sha(package/'assembly-report.json'),
        'vendor':assembly.get('vendor',{'kind':'legacy-locked','sha256':lock['vendor']['sha256']}),
        'status':'experimental local installation candidate; clean-install qualification pending',
        'redistribution':'Not approved: vendor and user-obtained Sony OEM remain local',
        'images':{name:{'sha256':sha(path),'bytes':path.stat().st_size} for name,path in sorted(images.items())}}


def flashing_instructions(oem_included=True, device_commit=None):
    text = """# XQ-BT52 local installation candidate

Experimental Ubuntu Touch 24.04, unlocked XQ-BT52, slot A only. Erases all userdata.
Use the firmware/bootloader baseline documented for the exact candidate. Firmware
compatibility is currently qualified only on the development device. Do not change
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
"""
    if not oem_included:
        if not isinstance(device_commit, str) or not re.fullmatch('[0-9a-f]{40}', device_commit):
            raise ValueError('Exact device source commit required for OEM preparation')
        text = text.replace('This local bundle\ncontains owner-obtained OEM/vendor inputs and must not be uploaded or redistributed.',
                            'Sony OEM is excluded from this archive and must be obtained separately.\nA CI build is not installation or firmware-baseline qualification.')
        preparation = """## Obtain and verify OEM separately

On Linux with Python 3, Git and Android platform-tools, download the v9a Lena
archive directly from Sony after accepting Sony's EULA. See the exact source
checkout's docs/OEM.md and docs/INSTALLATION-QUALIFICATION.md before flashing.
Do not flash the original sparse OEM directly: large FILL writes have hung.
The verifier below checks the pinned archive, member and decoded image and
converts FILL to RAW. It does not download or accept licence terms for you.

```sh
git clone https://github.com/Actinis/ut-device-sony-pdx213.git pdx213-sources
git -C pdx213-sources checkout --detach COMMIT
python3 pdx213-sources/tools/verify_sony_oem.py \\
  --archive /path/to/SW_binaries_for_Xperia_Android_11_4.19_v9a_lena.zip \\
  --output ./oem-original.img --fastboot-output ./oem.img
```

The separately generated OEM is validated by that verifier; SHA256SUMS covers
only the files supplied by this archive. Keep the original and derived OEM local.

""".replace('COMMIT', device_commit)
        text = text.replace('From this directory, verify checksums', preparation + 'From this directory, verify checksums')
    return text


def stage(images,manifest,destination,hardlink=False):
    destination.mkdir(mode=0o700,exist_ok=False)
    for name,path in images.items():
        if hardlink:os.link(path,destination/name)
        else:shutil.copyfile(path,destination/name)
    (destination/'install-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    files=list(images)+['install-manifest.json']
    (destination/'FLASHING.md').write_text(flashing_instructions())
    files.append('FLASHING.md')
    (destination/'SHA256SUMS').write_text(''.join(sha(destination/name)+'  '+name+'\n' for name in sorted(files)))


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
