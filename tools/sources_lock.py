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
    need(schema in (1,2,3,4,5),'Unknown lock schema')
    need(set(sources) == (REQUIRED | {'gnss','nfc','repowerd'} if schema==5 else REQUIRED | {'gnss','nfc'} if schema==4 else REQUIRED | {'gnss'} if schema==3 else REQUIRED if schema>=2 else {'kernel','rootfs','halium_gsi','toolchain'}),'Complete source inventory required')
    for name, entry in sources.items():
        kind=entry.get('kind') if schema>=2 else 'git' if name=='kernel' else 'artifact'
        need(kind in ('git','artifact','manual','derived'),'Unknown source kind')
        if kind!='derived':
            need(isinstance(entry.get('url'),str) and entry['url'].startswith('https://'),'HTTPS URL required')
        if kind=='git':
            need(bool(re.fullmatch('[0-9a-f]{40}',entry.get('commit',''))) and entry['commit']!='0'*40,'Exact git commit required')
        elif kind in ('artifact','manual'):
            need(bool(entry.get('version')) and bool(re.fullmatch('[0-9a-f]{64}',entry.get('sha256',''))),'Version and SHA256 required')
            if schema>=2:
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
                    need((Path(repository)/path).is_file(),'Missing tracked input: '+filename)
                    need(hashlib.sha256((Path(repository)/path).read_bytes()).hexdigest()==checksum,'Tracked input hash mismatch: '+filename)
    if schema>=3:
        gnss=sources['gnss']
        need(gnss.get('kind')=='derived' and set(gnss.get('dependencies',[]))=={'toolchain','rootfs','halium_gsi'},'Incomplete GNSS dependencies')
        need(bool(gnss.get('files')),'GNSS source hashes required')
        origins=gnss.get('origins',{})
        need(set(origins)=={'platform_api','hidl_interfaces','hidl_transport','vndk_headers','header_generator'},'GNSS origin inventory required')
        for origin in origins.values():
            need(isinstance(origin.get('url'),str) and origin['url'].startswith('https://'),'GNSS origin URL required')
            need(bool(re.fullmatch('[0-9a-f]{40}',origin.get('commit',''))),'GNSS origin commit required')
        if repository:
            import json
            provenance=json.loads((Path(repository)/'device/gnss/ORIGINS.json').read_text())
            for name,origin in origins.items():
                need(all(provenance[name].get(key)==value for key,value in origin.items()),'GNSS provenance mismatch: '+name)
            tracked={path.relative_to(repository).as_posix() for path in (Path(repository)/'device/gnss').rglob('*') if path.is_file()}
            need(tracked<=set(gnss['files']),'Unpinned GNSS source/header')
    if schema>=4:
        nfc=sources['nfc']
        need(nfc.get('kind')=='derived' and set(nfc.get('dependencies',[]))=={'gnss','toolchain','rootfs','halium_gsi'},'Incomplete NFC dependencies')
        need(bool(nfc.get('files')),'NFC input hashes required')
        if repository:
            import json
            base=Path(repository)/'device/nfc'
            tracked={p.relative_to(repository).as_posix() for p in base.rglob('*') if p.is_file()}
            need(tracked==set(nfc['files']),'Unpinned or stale NFC source inventory')
            validate_nfc_inputs(json.loads((base/'inputs.json').read_text()),base)
            origins=json.loads((base/'ORIGINS.json').read_text())
            for name in ('interfaces','vndk_headers','generator'):
                origin=origins.get(name,{})
                need(str(origin.get('url','')).startswith('https://') and bool(re.fullmatch('[0-9a-f]{40}',origin.get('commit',''))),'Invalid NFC header provenance')
    if schema>=5:
        entry=sources['repowerd']
        need(entry.get('kind')=='derived' and set(entry.get('dependencies',[]))=={'toolchain','rootfs'},'Incomplete Repowerd dependencies')
        need(bool(entry.get('files')),'Repowerd input hashes required')
        if repository:
            import json
            base=Path(repository)/'device/repowerd'
            tracked={p.relative_to(repository).as_posix() for p in base.rglob('*') if p.is_file()}
            need(tracked==set(entry['files']),'Unpinned or stale Repowerd source inventory')
            validate_repowerd_inputs(json.loads((base/'inputs.json').read_text()),base)
    return data


def validate_nfc_inputs(data, root=None):
    def need(condition,message):
        if not condition:raise ValueError(message)
    need(data.get('schema_version')==1,'Unknown NFC input schema')
    sources=data.get('sources',[])
    names=[e.get('component') for e in sources]
    need(len(names)==8 and set(names)=={'hal','binder-plugin','nci-plugin','ncicore','nfcd','ese','ese-nxp','ese-extns'},'Incomplete NFC git input inventory')
    for e in sources:
        need(str(e.get('url','')).startswith('https://') and bool(re.fullmatch('[0-9a-f]{40}',e.get('commit',''))),'Unpinned NFC git input')
        patched=e['component'] in {'hal','binder-plugin','nci-plugin','ncicore','nfcd'}
        need(('patch' in e)==patched,'Incomplete NFC patch inventory')
        if patched:
            need(e['patch']==e['component']+'.patch','Unsafe NFC patch filename')
            need(bool(re.fullmatch('[0-9a-f]{64}',e.get('patch_sha256',''))),'Missing NFC patch hash')
            if root:need(hashlib.sha256((Path(root)/e['patch']).read_bytes()).hexdigest()==e['patch_sha256'],'NFC patch hash mismatch')
    packages=data.get('development_headers',[])
    names=[e.get('name') for e in packages]
    need(len(names)==10 and len(set(names))==10,'Incomplete NFC package inventory')
    need(set(names)=={'libgbinder-dev','libglibutil-dev','libncicore-dev','libnciplugin-dev','libnfcd-dev','libnfcdef-dev','libc6-dev','libglib2.0-dev','linux-libc-dev','libglib2.0-dev-bin'},'Unknown NFC development package')
    for e in packages:
        need(bool(e.get('version')) and str(e.get('url','')).startswith('https://'),'Missing NFC package provenance')
        need(bool(re.fullmatch('[0-9a-f]{64}',e.get('sha256',''))),'Unpinned NFC package')
        name=e.get('filename','')
        need(bool(name) and Path(name).name==name and name not in ('.','..') and e['url'].endswith('/'+name),'Unsafe NFC package filename')
    return data


def validate_repowerd_inputs(data, root=None):
    def need(condition, message):
        if not condition: raise ValueError(message)
    need(data.get('schema_version')==1,'Unknown Repowerd input schema')
    source=data.get('source',{})
    need(str(source.get('url','')).startswith('https://') and bool(re.fullmatch('[0-9a-f]{40}',source.get('commit',''))) and source.get('commit')!='0'*40,'Unpinned Repowerd source')
    need(source.get('patch')=='raise-to-wake.patch' and bool(re.fullmatch('[0-9a-f]{64}',source.get('patch_sha256',''))),'Unpinned Repowerd patch')
    if root: need(hashlib.sha256((Path(root)/source['patch']).read_bytes()).hexdigest()==source['patch_sha256'],'Repowerd patch hash mismatch')
    packages=data.get('development_packages',[])
    expected={'libc6-dev','linux-libc-dev','libglib2.0-dev','libgbinder-dev','libglibutil-dev','android-headers','libdeviceinfo-dev','libhybris-common-dev','libhybris-dev','libandroid-properties-dev','libgcc-13-dev','libstdc++-13-dev','libffi-dev','libpcre2-dev','zlib1g-dev','libblkid-dev','libmount-dev','libselinux1-dev','libsepol-dev','uuid-dev'}
    names=[e.get('name') for e in packages]
    need(len(names)==len(expected) and set(names)==expected,'Incomplete Repowerd development package inventory')
    for entry in packages:
        name=entry.get('filename','')
        need(bool(entry.get('version')) and str(entry.get('url','')).startswith('https://'),'Missing Repowerd package provenance')
        need(bool(re.fullmatch('[0-9a-f]{64}',entry.get('sha256',''))),'Unpinned Repowerd package')
        need(bool(name) and Path(name).name==name and name not in ('.','..') and entry['url'].endswith('/'+name),'Unsafe Repowerd package filename')
    return data
