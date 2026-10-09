import copy
import importlib.util
import json
from pathlib import Path
import unittest
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from sources_lock import validate_repowerd_inputs
spec=importlib.util.spec_from_file_location('tilt',ROOT/'overlay/usr/local/sbin/utxperia-tilt')
# Extensionless installed scripts require an explicit source loader.
from importlib.machinery import SourceFileLoader
spec=importlib.util.spec_from_loader('tilt',SourceFileLoader('tilt',str(ROOT/'overlay/usr/local/sbin/utxperia-tilt')))
tilt=importlib.util.module_from_spec(spec);spec.loader.exec_module(tilt)

class RepowerdInputs(unittest.TestCase):
    def test_pins_reject_incomplete_or_unsafe_inputs(self):
        base=ROOT/'device/repowerd'
        data=json.loads((base/'inputs.json').read_text())
        validate_repowerd_inputs(data,base)
        for change in ('commit','patch','hash','package','url','filename','duplicate'):
            bad=copy.deepcopy(data)
            if change=='commit':bad['source']['commit']='main'
            if change=='patch':bad['source']['patch']='../outside.patch'
            if change=='hash':bad['source']['patch_sha256']='a'*64
            if change=='package':bad['development_packages'].pop()
            if change=='url':bad['development_packages'][0]['url']='http://example.org/a.deb'
            if change=='filename':bad['development_packages'][0]['filename']='../a.deb'
            if change=='duplicate':bad['development_packages'][-1]=bad['development_packages'][0]
            with self.subTest(change=change),self.assertRaises(ValueError):validate_repowerd_inputs(bad,base)

class TiltRegistry(unittest.TestCase):
    def original(self):
        node={'owner':'sns_tilt','enabled':{'type':'int','ver':'0','data':'1'},'future':{'data':'preserve'}}
        for key,value in {'sample_rate':'10','init_accel_window_time':'1','accel_window_time':'2','angle_threshold':'0.610865'}.items():
            node[key]={'type':'flt','ver':'0','data':value}
        return {'sns_tilt':node,'other':{'data':'preserve'}}
    def test_only_timing_fields_change(self):
        original=self.original();actual=tilt.tune(copy.deepcopy(original))
        self.assertEqual(actual['sns_tilt']['sample_rate']['data'],'25.000000')
        self.assertEqual(actual['sns_tilt']['init_accel_window_time']['data'],'0.300000')
        self.assertEqual(actual['sns_tilt']['accel_window_time']['data'],'0.400000')
        for key in ('sample_rate','init_accel_window_time','accel_window_time'):
            actual['sns_tilt'][key]['data']=original['sns_tilt'][key]['data']
        self.assertEqual(actual,original)
    def test_unsupported_registry_fails_before_mount(self):
        for value in ('nan','inf','0','-1','not-a-number'):
            data=self.original();data['sns_tilt']['sample_rate']['data']=value
            with self.subTest(value=value),self.assertRaises(ValueError):tilt.tune(data)
        data=self.original();data['sns_tilt']['enabled']['data']='0'
        with self.assertRaises(ValueError):tilt.tune(data)
        data=self.original();del data['sns_tilt']['angle_threshold']
        with self.assertRaises(KeyError):tilt.tune(data)
