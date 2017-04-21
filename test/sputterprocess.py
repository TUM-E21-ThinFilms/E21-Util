import unittest
from mock import Mock
from e21_util.error import CommunicationError
from e21_util.sputterprocess import SputterProcess
from e21_util.gunparameter import GunSelectionConfigParser
import time
import logging.handlers
import random

import devcontroller
from devcontroller.misc.thread import StoppableThread
from devcontroller.gun import GunController
from devcontroller.vat import VATController
from devcontroller.adl import ADLController
from devcontroller.trumpfrf import TrumpfPFG600Controller
from devcontroller.julabo import JulaboController
from devcontroller.shutter import ShutterController
from tpg26x.driver import PfeifferTPG26xDriver

class FakeTimer(object):
    def sleep(self, seconds):
        #return
        time.sleep(seconds/100.0)

class TestSputterProcess(unittest.TestCase):

    def test_nothing(self):
        self.assertTrue(True)

    def test_leak_valve(self):
        gun = Mock(GunController)
        vat_ar = Mock(VATController)
        vat_o2 = Mock(VATController)
        adl_a = Mock(ADLController)
        adl_b = Mock(ADLController)
        trumpfrf = Mock(TrumpfPFG600Controller)
        julabo = Mock(JulaboController)
        shutter = Mock(ShutterController)
        gauge = Mock(PfeifferTPG26xDriver)

        gun.get_gun.return_value = 2
        gauge.get_pressure_measurement.return_value=["Data Okay", 5e-5]

        adl_b.get_voltage.return_value = 40
        adl_b.get_power.return_value = 20

        logmsg = ""
        logger = logging.getLogger("test")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.handlers.MemoryHandler(1, target=logmsg))
        logger.addHandler(logging.StreamHandler())
        process = SputterProcess('test_variables', configparser=GunSelectionConfigParser("gun_selection.conf"), logger=logger, timer=FakeTimer())
        process.drivers(gun, vat_ar, vat_o2, adl_a, adl_b, trumpfrf, shutter, julabo, gauge)

        self.assertEqual(vat_ar, process.find_leak_valve('ar'))
        self.assertEqual(vat_ar, process.find_leak_valve('AR'))
        self.assertEqual(vat_ar, process.find_leak_valve('Ar'))
        self.assertEqual(vat_ar, process.find_leak_valve('aR'))

        self.assertEqual(vat_o2, process.find_leak_valve('o2'))
        self.assertEqual(vat_o2, process.find_leak_valve('O2'))

        self.assertRaises(RuntimeError, process.find_leak_valve, '02')

        #process.sputter('Dy', 'Ar', 3.0e-3, 10)

        process.sputter_sequence([['Dy', 'Ar', 3.0e-3, 100]])







if __name__ == '__main__':
    unittest.main()
