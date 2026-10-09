import importlib.util
import json
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('sources_lock',Path(__file__).resolve().parents[1]/'tools/sources_lock.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class Lock(unittest.TestCase):
    def test_repository_and_missing_dependencies(self):
        root=Path(__file__).resolve().parents[1]
        data=json.loads((root/'sources.lock.json').read_text())
        module.validate(data,root)
        for name in list(data['sources']):
            bad=json.loads(json.dumps(data));del bad['sources'][name]
            with self.assertRaises(ValueError):module.validate(bad)
    def test_wrong_release_and_unpinned_git(self):
        data=json.loads((Path(__file__).resolve().parents[1]/'sources.lock.json').read_text())
        data['ubuntu_touch']='20.04'
        with self.assertRaises(ValueError):module.validate(data)
        data['ubuntu_touch']='24.04';data['sources']['kernel']['commit']='0'*40
        with self.assertRaises(ValueError):module.validate(data)
