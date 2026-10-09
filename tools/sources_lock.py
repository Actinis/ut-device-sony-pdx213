"""Versioned source-lock validation shared by CI, builds and release metadata."""
import hashlib
import re
from pathlib import Path

REQUIRED = {'kernel','rootfs','halium_gsi','toolchain','initrd','mkbootimg','vendor','sony_oem','boot_metadata','dtb','auxiliary','rootfs_tools'}
def validate(data, repository=None):
    def need(condition, message):
        if not condition: raise ValueError(message)
    need(data.get('ubuntu_touch') == '24.04' and data.get('device') == 'sony-pdx213', 'Only pdx213 Noble is supported')
    need(data.get('status') == 'locked', 'Sources are not locked')
    sources=data.get('sources',{})
    schema=data.get('schema_version')
    need(schema in (1,2),'Unknown lock schema')
    need(set(sources) == (REQUIRED if schema==2 else {'kernel','rootfs','halium_gsi','toolchain'}),'Complete source inventory required')
    for name, entry in sources.items():
        kind=entry.get('kind') if schema==2 else 'git' if name=='kernel' else 'artifact'
        need(kind in ('git','artifact','manual','derived'),'Unknown source kind')
        if kind!='derived':
            need(isinstance(entry.get('url'),str) and entry['url'].startswith('https://'),'HTTPS URL required')
        if kind=='git':
            need(bool(re.fullmatch('[0-9a-f]{40}',entry.get('commit',''))) and entry['commit']!='0'*40,'Exact git commit required')
        elif kind in ('artifact','manual'):
            need(bool(entry.get('version')) and bool(re.fullmatch('[0-9a-f]{64}',entry.get('sha256',''))),'Version and SHA256 required')
            if schema==2:
                filename=entry.get('filename','')
                need(filename and Path(filename).name==filename and filename not in ('.','..'),'Safe input filename required')
            if kind=='manual':need(bool(entry.get('acquisition')) and bool(entry.get('redistribution')),'Manual input constraints required')
        else:
            need(isinstance(entry.get('dependencies'),list) and set(entry['dependencies'])<=set(sources),'Invalid derived dependency')
            need(bool(entry.get('description')),'Derived provenance required')
            for filename, checksum in entry.get('files',{}).items():
                path=Path(filename)
                need(not path.is_absolute() and '..' not in path.parts,'Unsafe tracked source path')
                need(bool(re.fullmatch('[0-9a-f]{64}',checksum)),'Tracked file hash required')
                if repository:
                    need(hashlib.sha256((Path(repository)/path).read_bytes()).hexdigest()==checksum,'Tracked input hash mismatch: '+filename)
    return data
