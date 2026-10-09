import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
class APN(unittest.TestCase):
    def run_helper(self, modems, contexts):
        class Failure(Exception): pass
        class Manager:
            def GetModems(self,timeout):return modems
        class Modem:
            def GetContexts(self,timeout):return contexts
        class Bus:
            def get_object(self,name,path):return Manager() if path=='/' else Modem()
        fake=types.SimpleNamespace(SystemBus=Bus, Interface=lambda obj,iface:obj, DBusException=Failure)
        spec=importlib.util.spec_from_file_location('apn',ROOT/'overlay/usr/local/lib/utxperia/gnss_active_apn.py')
        helper=importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules,{'dbus':fake}),patch('builtins.print') as output:
            spec.loader.exec_module(helper)
            helper.main()
            return output.call_args.args[0]
    def test_only_active_ipv4_internet_is_selected(self):
        modem=[('/modem',{'Online':True,'Interfaces':['org.ofono.ConnectionManager']})]
        entries=[('/ims',{'Active':True,'Type':'ims','AccessPointName':'ims','Settings':{'Address':'192.0.2.1'}}),
                 ('/inactive',{'Active':False,'Type':'internet','AccessPointName':'stale'}),
                 ('/active',{'Active':True,'Type':'internet','AccessPointName':'example.apn','Settings':{'Address':'192.0.2.2'}})]
        self.assertEqual(self.run_helper(modem,entries),'example.apn')
    def test_missing_ambiguous_and_offline_fail_closed(self):
        online=[('/modem',{'Online':True,'Interfaces':['org.ofono.ConnectionManager']})]
        active=('/active',{'Active':True,'Type':'internet','AccessPointName':'example.apn','Settings':{'Address':'192.0.2.2'}})
        for modems,ctx in [([],[]),(online,[]),(online,[active,active]),
                           ([('/modem',{'Online':False})],[active]),
                           (online,[('/v6',{'Active':True,'Type':'internet','AccessPointName':'example.apn','Settings':{}})])]:
            with self.assertRaises(SystemExit):self.run_helper(modems,ctx)
