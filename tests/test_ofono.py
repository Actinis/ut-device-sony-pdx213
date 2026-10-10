import copy
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from sources_lock import validate_ofono_inputs
from build_ofono import artifact_hashes


class RadioInputs(unittest.TestCase):
    def test_reject_unpinned_or_incomplete_inputs(self):
        base = ROOT / 'device/ofono'
        data = json.loads((base / 'inputs.json').read_text())
        validate_ofono_inputs(data, base)
        for change in ('source', 'packaging', 'patch', 'hash', 'packages', 'duplicate', 'filename', 'runtime'):
            bad = copy.deepcopy(data)
            if change == 'source': bad['source']['commit'] = 'main'
            if change == 'packaging': bad['packaging']['commit'] = '0' * 40
            if change == 'patch': bad['patch']['file'] = '../other.patch'
            if change == 'hash': bad['patch']['sha256'] = 'a' * 64
            if change == 'packages': bad['development_packages'].pop()
            if change == 'duplicate': bad['development_packages'][-1] = bad['development_packages'][0]
            if change == 'filename': bad['development_packages'][0]['filename'] = '../a.deb'
            if change == 'runtime': bad['runtime_libraries'].pop('libgbinder-radio.so.1')
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_ofono_inputs(bad, base)

    def test_actual_patch_expression_across_radio_versions(self):
        patch = (ROOT / 'device/ofono/screen-off-filter.patch').read_text()
        added = '\n'.join(line[1:] for line in patch.splitlines() if line.startswith('+') and not line.startswith('+++'))
        expr = re.search(r'const RADIO_IND_FILTER value = (.*?);', added, re.S).group(1)
        harness = '''#include <stdint.h>
#include <assert.h>
typedef uint32_t RADIO_IND_FILTER;
#define RADIO_IND_FILTER_DATA_CALL_DORMANCY 4
struct monitor { int display_on; }; struct interface { uint32_t ind_filter_all; };
static uint32_t filter(struct monitor *self, struct interface *api) { return EXPRESSION; }
int main(void) {
 struct monitor monitor; struct interface api;
 uint32_t versions[] = { 0x1f, 0x7f, 0xffffffff };
 for (unsigned i=0; i<3; i++) {
  api.ind_filter_all=versions[i]; monitor.display_on=0;
  assert(filter(&monitor,&api)==4);
  monitor.display_on=1; assert(filter(&monitor,&api)==versions[i]);
  monitor.display_on=0; assert(filter(&monitor,&api)==4);
 }
 return 0;
}
'''
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'filter.c'; binary = Path(directory) / 'filter'
            source.write_text(harness.replace('EXPRESSION', expr))
            subprocess.run(['cc', '-Wall', '-Werror', str(source), '-o', str(binary)], check=True)
            subprocess.run([str(binary)], check=True)

    def test_artifacts_reject_missing_and_linked_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            (out / 'binderplugin.so').write_bytes(b'plugin')
            with self.assertRaises(ValueError): artifact_hashes(out)
            (out / 'licences').mkdir(); (out / 'licences/LICENSE').write_text('licence')
            original = artifact_hashes(out)
            (out / 'binderplugin.so').write_bytes(b'changed plugin')
            self.assertNotEqual(original, artifact_hashes(out))
            (out / 'binderplugin.so').unlink(); (out / 'binderplugin.so').symlink_to('licences/LICENSE')
            with self.assertRaises(ValueError): artifact_hashes(out)
