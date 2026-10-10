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
    need(schema in (1,2,3,4,5,6,7,8),'Unknown lock schema')
    need(set(sources) == (REQUIRED | {'gnss','nfc','repowerd','vendor_recipe','repo_tool','avbtool','ofono'} | ({'camera'} if schema == 8 else set()) if schema>=7 else REQUIRED | {'gnss','nfc','repowerd','vendor_recipe','repo_tool','avbtool'} if schema==6 else REQUIRED | {'gnss','nfc','repowerd'} if schema==5 else REQUIRED | {'gnss','nfc'} if schema==4 else REQUIRED | {'gnss'} if schema==3 else REQUIRED if schema>=2 else {'kernel','rootfs','halium_gsi','toolchain'}),'Complete source inventory required')
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
    vendor=sources.get('vendor',{})
    if 'build_report' in vendor:
        report=vendor['build_report']
        need(vendor.get('kind')=='artifact' and isinstance(report,dict),'Vendor report requires artifact input')
        need(report.get('kind')=='artifact' and bool(report.get('version')),'Pinned vendor report artifact required')
        need(isinstance(report.get('url'),str) and report['url'].startswith('https://'),'Vendor report HTTPS URL required')
        need(bool(re.fullmatch('[0-9a-f]{64}',report.get('sha256',''))),'Vendor report SHA256 required')
        filename=report.get('filename','')
        need(filename and Path(filename).name==filename and filename not in ('.','..') and filename!=vendor.get('filename'),'Distinct safe vendor report filename required')
        need(type(report.get('bytes')) is int and report['bytes']>0,'Vendor report size required')
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
    if schema >= 6:
        entry=sources['vendor_recipe']
        need(entry.get('kind')=='derived' and set(entry.get('dependencies',[]))=={'repo_tool'},'Invalid vendor recipe dependencies')
        need(bool(entry.get('files')),'Missing vendor recipe inventory')
        if repository:
            import json
            import sys
            sys.path.insert(0,str(Path(repository)/'tools'))
            from build_vendor import projects
            projects(Path(repository)/'device/vendor/manifest.xml')
            expected={str(p.relative_to(repository)) for p in (Path(repository)/'device/vendor').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
            expected.add('tools/build_vendor.py')
            need(set(entry['files'])==expected,'Incomplete vendor recipe file inventory')
        oem=sources['sony_oem']
        archive=oem.get('archive',{})
        need(oem.get('kind')=='manual' and oem.get('format')=='android-sparse','OEM must remain a manual sparse image')
        need(bool(re.fullmatch('[0-9a-f]{64}',oem.get('decoded_sha256',''))) and isinstance(oem.get('decoded_bytes'),int) and oem['decoded_bytes']>0,'Missing OEM decoded image identity')
        name=archive.get('filename','')
        need(name and Path(name).name==name and name not in ('.','..') and bool(re.fullmatch('[0-9a-f]{64}',archive.get('sha256',''))),'Missing OEM archive identity')
        need(sources['avbtool'].get('kind')=='artifact' and sources['avbtool'].get('encoding')=='base64' and bool(re.fullmatch('[0-9a-f]{64}',sources['avbtool'].get('decoded_sha256',''))),'AVB utility must be checksum-pinned before and after decoding')
    if schema >= 7:
        entry = sources['ofono']
        need(entry.get('kind') == 'derived' and set(entry.get('dependencies', [])) == {'toolchain', 'rootfs'}, 'Incomplete oFono dependencies')
        need(bool(entry.get('files')), 'Missing oFono input inventory')
        if repository:
            import json
            base = Path(repository) / 'device/ofono'
            expected = {p.relative_to(repository).as_posix() for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
            expected.add('tools/build_ofono.py')
            need(set(entry['files']) == expected, 'Unpinned or stale oFono source inventory')
            validate_ofono_inputs(json.loads((base / 'inputs.json').read_text()), base)
    if schema >= 8:
        entry = sources['camera']
        need(entry.get('kind') == 'derived' and set(entry.get('dependencies', [])) == {'toolchain', 'rootfs'}, 'Incomplete camera dependencies')
        if repository:
            import json
            base = Path(repository) / 'device/camera'
            expected = {p.relative_to(repository).as_posix() for p in base.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
            expected.add('tools/build_camera.py')
            need(set(entry.get('files', {})) == expected, 'Incomplete camera source inventory')
            validate_camera_inputs(json.loads((base / 'inputs.json').read_text()), base)
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


def validate_ofono_inputs(data, root=None):
    def need(condition, message):
        if not condition: raise ValueError(message)
    need(data.get('schema_version') == 1, 'Unknown oFono input schema')
    for key in ('source', 'packaging'):
        entry = data.get(key, {})
        need(str(entry.get('url', '')).startswith('https://') and bool(re.fullmatch('[0-9a-f]{40}', entry.get('commit', ''))) and entry['commit'] != '0' * 40, 'Unpinned oFono source')
    patch = data.get('patch', {})
    packaging = data['packaging']
    need(patch.get('file') == 'screen-off-filter.patch' and packaging.get('patch') == 'ubports-mtk.patch', 'Unsafe oFono patch path')
    for name, checksum in ((patch['file'], patch.get('sha256', '')), (packaging['patch'], packaging.get('patch_sha256', ''))):
        need(bool(re.fullmatch('[0-9a-f]{64}', checksum)), 'Missing oFono patch checksum')
        if root: need(hashlib.sha256((Path(root) / name).read_bytes()).hexdigest() == checksum, 'oFono patch hash mismatch')
    need(bool(re.fullmatch('[0-9a-f]{64}', data.get('original_plugin_sha256', ''))), 'Unpinned original oFono plugin')
    packages = data.get('development_packages', [])
    expected = {'libc6-dev', 'linux-libc-dev', 'libglib2.0-dev', 'libffi-dev', 'libpcre2-dev', 'libgbinder-dev', 'libglibutil-dev', 'ofono-sailfish-dev', 'libgbinder-radio1-dev', 'libmce-glib-dev', 'libdbus-1-dev', 'libgcc-13-dev'}
    names = [entry.get('name') for entry in packages]
    need(len(names) == len(expected) and set(names) == expected, 'Incomplete oFono development package inventory')
    for entry in packages:
        name = entry.get('filename', '')
        need(bool(entry.get('version')) and str(entry.get('url', '')).startswith('https://'), 'Missing oFono package provenance')
        need(bool(re.fullmatch('[0-9a-f]{64}', entry.get('sha256', ''))), 'Unpinned oFono package')
        need(bool(name) and Path(name).name == name and name not in ('.', '..') and entry['url'].endswith('/' + name), 'Unsafe oFono package filename')
    libraries = data.get('runtime_libraries', {})
    need(set(libraries) == {'libgbinder-radio.so.1', 'libgbinder.so.1', 'libmce-glib.so.1', 'libglibutil.so.1', 'libgobject-2.0.so.0', 'libglib-2.0.so.0', 'libofonobinderpluginext.so.1'}, 'Incomplete oFono runtime inventory')
    need(all(re.fullmatch('[0-9a-f]{64}', checksum) for checksum in libraries.values()), 'Unpinned oFono runtime library')
    return data


def validate_camera_inputs(data, root=None):
    def need(condition, message):
        if not condition: raise ValueError(message)
    need(data.get('schema_version') == 1, 'Unknown camera input schema')
    source = data.get('source', {})
    need(str(source.get('url', '')).startswith('https://') and bool(re.fullmatch('[0-9a-f]{40}', source.get('commit', ''))) and source['commit'] != '0' * 40, 'Unpinned camera source')
    need(source.get('patch') == 'qt-microphone-start.patch' and bool(re.fullmatch('[0-9a-f]{64}', source.get('patch_sha256', ''))), 'Unpinned camera patch')
    if root: need(hashlib.sha256((Path(root) / source['patch']).read_bytes()).hexdigest() == source['patch_sha256'], 'Camera patch hash mismatch')
    need(bool(re.fullmatch('[0-9a-f]{64}', data.get('original_plugin_sha256', ''))), 'Unpinned camera distribution baseline')
    need(data.get('moc') == {'path': 'usr/lib/qt5/bin/moc', 'version': 'moc 5.15.13'}, 'Unpinned or unsafe Qt generator')
    packages = data.get('development_packages', [])
    expected = {'libstdc++-13-dev', 'libqt5sensors5-dev', 'libegl-dev', 'libpulse-dev', 'libhybris-dev', 'libglvnd-dev', 'libgcc-13-dev', 'qtmultimedia5-dev', 'libqt5opengl5-dev', 'libhybris-common-dev', 'libmedia-dev', 'libqtubuntu-media-signals-dev', 'libdeviceinfo-dev', 'android-headers-19', 'libandroid-properties-dev', 'libexiv2-dev', 'libgl-dev', 'qtbase5-dev-tools', 'qtbase5-dev', 'libgles-dev', 'linux-libc-dev', 'libc6-dev'}
    names = [entry.get('name') for entry in packages]
    need(len(names) == len(expected) and set(names) == expected, 'Incomplete camera development package inventory')
    for entry in packages:
        name = entry.get('filename', '')
        need(bool(entry.get('version')) and str(entry.get('url', '')).startswith('https://'), 'Missing camera package provenance')
        need(bool(re.fullmatch('[0-9a-f]{64}', entry.get('sha256', ''))), 'Unpinned camera package')
        need(bool(name) and Path(name).name == name and name not in ('.', '..') and entry['url'].endswith('/' + name), 'Unsafe camera package filename')
    return data
