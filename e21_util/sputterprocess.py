import time
import datetime
import logging
import os.path
import errno

from logging.handlers import SMTPHandler
from e21_util.gunparameter import GunSelectionConfigParser, GunSelectionConfig

from devcontroller.misc.thread import StoppableThread
from devcontroller.gun import GunController
from devcontroller.vat import VATController
from devcontroller.adl import ADLController
from devcontroller.trumpfrf import TrumpfPFG600Controller
from devcontroller.julabo import JulaboController
from devcontroller.shutter import ShutterController
from devcontroller.lakeshore import LakeshoreController
from tpg26x.driver import PfeifferTPG26xDriver

class SputterProcess(object):
    DEFAULT_LOGGING_DIRECTORY = "/home/sputter/Python/scripts/log/"
    DEFAULT_IGNITION_PRESSURE = 6e-3  # mbar
    DEFAULT_SPUTTER_POWER = 20  # Watt
    DEFAULT_PRE_SPUTTER_POWER = 50  # Watt
    DEFAULT_PRE_SPUTTER_TIME = 10  # minutes
    GUN_CHANGING_ITERATIONS = 22  # number of iterations
    GUN_CHANGING_WAIT_TIME = 15  # seconds

    GAS_TYPE_UNK = -1
    GAS_TYPE_AR = 0
    GAS_TYPE_O2 = 1

    def __init__(self, process_name, timer=None, configparser = None, logger=None):
        self._name = process_name
        self._logger = logger
        if configparser is None:
            configparser = GunSelectionConfigParser()
        self._configParser = configparser
        self.load_config()
        if timer is None:
            timer = time
        self._timer = timer
        self._leak_valve_type = None
        self.create_logger()
        self._reignition_count = 0
        self._reignition_threshold = 3

    def drivers(self, gun, vat_ar, vat_o2, adl_a, adl_b, trumpfrf, shutter, julabo, gauge, lakeshore):
        self._gun = gun
        self._vat_ar = vat_ar
        self._vat_o2 = vat_o2
        self._adl_a = adl_a
        self._adl_b = adl_b
        self._trumpfrf = trumpfrf
        self._julabo = julabo
        self._gauge = gauge
        self._shutter = shutter
        self._lakeshore = lakeshore

        self._check_drivers()

    def _check_drivers(self):
        assert isinstance(self._gun, GunController)
        assert isinstance(self._vat_ar, VATController)
        assert isinstance(self._vat_o2, VATController)
        assert isinstance(self._adl_a, ADLController)
        assert isinstance(self._adl_b, ADLController)
        assert isinstance(self._trumpfrf, TrumpfPFG600Controller)
        assert isinstance(self._julabo, JulaboController)
        assert isinstance(self._shutter, ShutterController)
        assert isinstance(self._lakeshore, LakeshoreController)
        assert isinstance(self._gauge, PfeifferTPG26xDriver)  # TODO: might be changed to a GaugeController?

    def create_logger(self):

        if not self._logger is None:
            return

        # e.g. DbTy_MgO.log
        filepath = self.DEFAULT_LOGGING_DIRECTORY + self._name + ".log"
        try:
            os.makedirs(os.path.dirname(self.DEFAULT_LOGGING_DIRECTORY + self._name))
        except OSError as exc:
            if exc.errno == errno.EEXIST:
                pass
            else:
                raise

        if os.path.isfile(filepath):
            raise RuntimeError("Name already exists. Choose a different name.")

        self._logger = logging.getLogger('Sputter process')
        self._logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh = logging.FileHandler(filepath)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)
        toaddrs = ['alexander.book@frm2.tum.de', 'Jingfan.Ye@frm2.tum.de']
        # mailhandler = SMTPHandler(('smtp.frm2.tum.de', 587), 'sputterpc.e21@frm2.tum.de', toaddrs, 'Sputter-PC Message', ('sputterpc.e21', 'pw'))
        # mailhandler.setFormatter(formatter)
        # mailhandler.setLevel(logging.WARNING)
        self._logger.addHandler(fh)
        # self.logger.addHandler(mailhandler)

    def load_config(self):
        self._config = self._configParser.get_config()

    def find_gun_in_config(self, material):
        for i in range(1, self._config.get_gun_number() + 1):
            if material == self._config.get_gun_target(i):
                self._logger.info("Gun with number %s matches the material '%s'", i, material)
                return i

        raise RuntimeError(
            "Could not find gun with material '" + material + "' . Maybe update material configuration via the parameter/parameter_small interface")

    def select_gun(self, gun_number):

        self._logger.info("Selecting gun with number %s", gun_number)
        i = 0

        self._gun.set_gun(gun_number)

        while True:
            if i >= self.GUN_CHANGING_ITERATIONS:
                break

            try:
                current_gun = self._gun.get_gun()
            except:
                self._logger.info("Could not get current gun position...")
                current_gun = -1

            if current_gun == gun_number:
                self._logger.info("Gun in place.")
                try:
                    self._gun.clear()
                    self._gun.stop()
                except BaseException as e:
                    self.logger.error("Could not send stop command to gun!")
                    raise e
                return
            else:
                self._logger.info("Gun not in place. Iteration %s of %s", i, self.GUN_CHANGING_ITERATIONS)
                self._timer.sleep(self.GUN_CHANGING_WAIT_TIME)
            i = i + 1

        # wait time can be increased by gun_changing_iterations, gun_changing_wait_time
        raise RuntimeError("Could not move gun to desired gun position " + str(
            gun_number) + " in time. Maybe re-calibrate gun via calibrate() or increase waiting time?")

    def find_leak_valve(self, gas_name):
        if gas_name.lower() == 'ar':
            self._logger.info("Selected argon as gas")
            self._leak_valve_type = self.GAS_TYPE_AR
            return self._vat_ar
        elif gas_name.lower() == 'o2':
            self._logger.info("Selected oxygen as gas")
            self._leak_valve_type = self.GAS_TYPE_O2
            return self._vat_o2
        else:
            self._logger.warning("Unknown gas type")
            raise RuntimeError("Unknown gas type " + gas_name)

    def find_sputter_device(self, gun_number):
        gun_device = self._config.get_gun_sputter(gun_number)

        if gun_device == GunSelectionConfig.SPUTTER_DEVICE_ADL_A:
            self._logger.info("Using sputter device ADL-A")
            return self._adl_a
        elif gun_device == GunSelectionConfig.SPUTTER_DEVICE_ADL_B:
            self._logger.info("Using sputter device ADL-B")
            return self._adl_b
        elif gun_device == GunSelectionConfig.SPUTTER_DEVICE_TRUMPF_RF:
            self._logger.info("Using sputter device Trumpf RF")
            return self._trumpfrf
        else:
            raise RuntimeError("Could not determine sputter device. ")

    class PlasmaChecker(StoppableThread):
        def __init__(self, sputter_device, logger, timer):
            self._device = sputter_device
            self._logger = logger
            self._timer = timer
            self._reignite_count = 0
            self._reignite_threshold = 5
            self._do_reignition = False
            super(SputterProcess.PlasmaChecker, self).__init__()

        def on(self):
            self.daemon = True
            self._logger.info("Turning plasma checker on")
            self.start()

        def off(self):
            try:
                self._logger.info("Turning plasma checker off")
                self.stop()
            except BaseException as e:
                self._logger.warning("Exception while turning plasma checker off.")

        def do_execute(self):
            try:
                if not self.check():
                    self._reignite()

            except BaseException as e:
                self._logger.warning("Exception while checking plasma ignition.")
                self._logger.exception(e)

            self._timer.sleep(10)

        def check(self):
            if isinstance(self._device, ADLController):
                voltage = self._device.get_voltage()
                if voltage > 900:
                    self._logger.warning("Voltage at %s V. Probably no ignition")
                    return False
                else:
                    try:
                        power = self._device.get_power()
                    except:
                        power = "Unk."

                    self._logger.info("### --> Plasma Checker: ADL: %s Volt at %s Watt", voltage, power)
                    return True

            elif isinstance(self._device, TrumpfPFG600Controller):
                power_forward, power_backward = float(self._device.get_power_forward()), float(
                    self._device.get_power_backward())

                if power_forward > 0.01 and power_backward / power_forward > 0.5:
                    self._logger.warning("Power backward/Power forward = %s/%s > 0.5. Probably no ignition",
                                         power_backward, power_forward)
                    return False
                else:
                    try:
                        voltage = self._device.get_voltage()
                    except:
                        voltage = "Unk."

                    self._logger.info("### --> Plasma Checker: TrumpfRF: %s Volt at %s Watt", voltage, power_forward)
                    return True
            else:
                self._logger.error("Unknown sputter device.")
                self.off()
                return False

        def _reignite(self):
            self._reignite_count += 1

            if self._reignite_count > self._reignite_threshold:
                self._do_reignition = True
                self._reignite_count = 0

        def reset_reignition_counter(self):
            self._reignite_count = 0
            self._do_reignition = False

        def check_for_reignition(self):
            return self._do_reignition


    def _check_parameters(self, pressure, sputter_time, ignition_pressure, pre_power, pre_time, power):
        pass

    def sputter(self, material, gas, pressure, sputter_time,
                    ignition_pressure=None, pre_power=None, pre_time=None, power=None):

        if ignition_pressure is None or ignition_pressure <= 0:
            self._logger.info("No ignition pressure set, using the sputter pressure %s mbar", pressure)
            ignition_pressure = pressure

        if pre_power is None:
            self._logger.info("No pre-sputter power set. Using the default pre-sputter power of %s Watt",
                              self.DEFAULT_PRE_SPUTTER_POWER)
            pre_power = self.DEFAULT_PRE_SPUTTER_POWER

        if pre_time is None:
            self._logger.info("No pre-sputter time set. Using the default pre-sputter timer of %s minutes",
                              self.DEFAULT_PRE_SPUTTER_TIME)
            pre_time = self.DEFAULT_PRE_SPUTTER_TIME

        if power is None:
            self._logger.info("No sputter power set. Using the default sputter power of %s Watt",
                              self.DEFAULT_SPUTTER_POWER)
            power = self.DEFAULT_SPUTTER_POWER

        self._check_parameters(pressure, sputter_time, ignition_pressure, pre_power, pre_time, power)
        self._check_drivers()

        #self._logger.info("Sputter process: Ignition process: ")
        self._logger.info(
            "Sputtering process started. Using material %s @ (%s Watt, %s mbar) for %s seconds",
            material, power, pressure, sputter_time)

        gun_number = self.find_gun_in_config(material)
        valve = self.find_leak_valve(gas)
        sputter = self.find_sputter_device(gun_number)

        self._julabo.on()
        self._logger.info("Continuing in five seconds...")
        self._timer.sleep(5)

        self.select_gun(gun_number)
        self._logger.info("Gun positioned.")

        plasma_checker = SputterProcess.PlasmaChecker(sputter, self._logger, self._timer)

        try:

            self._sputter_ignition(ignition_pressure, pre_power, sputter, valve)
            plasma_checker.on()
            self._sputter_presputter(pre_power, pre_time, pressure, valve, ignition_pressure, sputter, plasma_checker)
            self._sputter_dosputter(power, pressure, sputter, sputter_time)
            plasma_checker.off()
            self._turn_off(sputter, valve)

        except BaseException as e:
            self._turn_off(sputter, valve)
            self._logger.error(
                "Exception while sputtering at " + str(datetime.datetime.now()) + ". Turned everything off immediately")
            self._logger.exception(e)

            raise e

        self._logger.info(
            "Sputter process finished. Used material %s @ (%s Watt, %s mbar) for %s seconds",
            material, power, pressure, sputter_time)

    def _turn_off(self, sputter, valve):
        try:
            self._logger.info("Turning off sputter device")
            sputter.off()
            self._logger.info("Closing valve")
            valve.close()
            self._logger.info("Turned off sputter device and closed valve.")
        except BaseException as e:
            self._logger.critical(
                "Exception while closing valve or turning sputter off. Turn these devices manually off!")
            self._logger.exception(e)
            raise e

    def _sputter_dosputter(self, power, pressure, sputter, sputter_time):
        self._logger.info("Sputter process started at %s", datetime.datetime.now())
        self._logger.info("--> Sputter parameter: Using pressure %s (mbar)", pressure)
        self._logger.info("--> Sputter parameter: Using power %s (Watt)", power)
        self._logger.info("--> Sputter parameter: Using timer %s (seconds)", sputter_time)
        self._logger.info("--> Sputter process: Setting power")
        self._sputter_on(power, sputter)
        self._logger.info("--> Sputter process: Waiting 5 seconds to stabilize the sputter power")
        self._timer.sleep(5)
        try:
            self._logger.info("--> Sputter process: Current pressure %s (mbar)",
                              self._gauge.get_pressure_measurement()[1])
        except:
            self._logger.info("--> Sputter process: Current pressure unknown")

        try:
            self._logger.info("--> Sputter process: Current temperature %s K at position C", self._lakeshore.get_temperature('C'))
        except:
            self._logger.info("--> Sputter process: Could not determine temperature")


        self._logger.info("--> Sputter process: Opening shutter now %s", datetime.datetime.now())
        self._shutter.timer(sputter_time)
        self._logger.info("--> Sputter process: Shutter closed %s", datetime.datetime.now())
        self._logger.info("--> Sputter process: Waiting 2 seconds for the shutter to fully close")
        self._timer.sleep(2)
        self._logger.info("Sputter process finished at %s", datetime.datetime.now())

    def _sputter_on(self, power, sputter):
        retries = 3
        for i in range(0, retries):
            try:
                sputter.power(power)
                sputter.on()
                self._timer.sleep(1)
                break
            except BaseException as e:
                if i == retries - 1:
                    self._logger.error("Could not set sputter power. Aborting...")
                    self._logger.exception(e)
                    raise e
                else:
                    self._logger.info("Could not set sputter power. Retry %s of %s", (i + 1), retries)

    def _sputter_presputter(self, pre_power, pre_time, pressure, valve, ignition_pressure, sputter, plasma_checker):
        self._logger.info("Pre-sputter process started")
        self._logger.info("--> Pre-sputter parameter: Using pressure %s (mbar)", pressure)
        self._logger.info("--> Pre-sputter parameter: Using power %s (Watt)", pre_power)
        self._logger.info("--> Pre-sputter parameter: Using timer %s (minutes)", pre_time)
        self._logger.info("--> Pre-sputter process: Setting pressure")
        valve.set_pressure(pressure)
        self._logger.info("--> Pre-sputter process: Waiting %s minutes, %s", pre_time, datetime.datetime.now())

        # waits in total pre_time * 6 * 10 seconds = pre_time minutes
        for i in range(0, pre_time * 6):
            self._timer.sleep(10)
            self._do_reignite(ignition_pressure, pressure, pre_power, sputter, valve, plasma_checker)

        self._logger.info("--> Pre-sputter process: Finished pre-sputtering")
        self._logger.info("Pre-sputter process finished")

    def _sputter_ignition(self, ignition_pressure, pre_power, sputter, valve, ignition_wait_time = 300):
        ignition_time = 20

        self._logger.info("Ignition process started")
        self._logger.info("--> Ignition parameter: Using ignition pressure %s (mbar)", ignition_pressure)
        self._logger.info("--> Ignition parameter: Using ignition power %s (Watt)", pre_power)
        self._logger.info("--> Ignition parameter: Using ignition timer %s (seconds)", ignition_time)
        self._logger.info("--> Ignition process: Base pressure at %s mbar", self._gauge.get_pressure_measurement()[1])
        self._logger.info("--> Ignition process: Setting pressure and waiting 15 seconds")
        valve.set_pressure(ignition_pressure)
        self._timer.sleep(15)

        if self._leak_valve_type == self.GAS_TYPE_O2 and ignition_wait_time > 0:
            self._logger.info("--> Ignition process: Waiting "+str(ignition_wait_time)+" seconds for the correct O_2 ratio")
            self._timer.sleep(ignition_wait_time)

        self._logger.info("--> Ignition process: Starting pre-sputtering with pressure %s",
                          self._gauge.get_pressure_measurement()[1])
        self._logger.info("--> Ignition process: Turning sputter device on")
        self._sputter_on(pre_power, sputter)
        self._logger.info("--> Ignition process: Sputter device turned on. Waiting for ignition timer")
        self._timer.sleep(ignition_time)
        self._logger.info("Ignition process finished")

    def _do_reignite(self, ignition_pressure, sputter_pressure, pre_power, sputter, valve, plasma_checker):

        if not plasma_checker.check_for_reignition():
            return True

        self._reignition_count += 1

        if self._reignition_count > self._reignition_threshold:
            self._logger.error("Aborting after %s reignition cycles", self._reignition_threshold)
            raise RuntimeError("Could not reignite sputter process")

        self._logger.info("Starting to reignite plasma. Current reignition counter %s of %s", self._reignition_count,
                          self._reignition_threshold)

        result = self._reignition_process(ignition_pressure, sputter_pressure, pre_power, sputter, valve, plasma_checker)

        if not result:
            self._do_reignite(ignition_pressure, sputter_pressure, pre_power, sputter, valve, plasma_checker)
        else:
            plasma_checker.reset_reignition_counter()

    def _reignition_process(self, ignition_pressure, sputter_pressure, pre_power, sputter, valve, plasma_checker):

        self._logger.info("Reignition process started")
        self._logger.info("--> Reignition process: Turn off sputter power supply")
        sputter.off()
        self._logger.info("--> Reignition process: Setting ignition pressure % (mbar)", ignition_pressure)
        valve.set_pressure(ignition_pressure)
        self._timer.sleep(15)
        self._logger.info("--> Reignition process: Turn on sputter power supply at %s (Watt)", pre_power)
        sputter.power(pre_power)
        sputter.on()
        self._logger.info("--> Reignition process: Checking plasma in 30 seconds...")
        self._timer.sleep(30)
        try:
            result = plasma_checker.check()
        except:
            self._logger.warning("Could not check plasma in reignition process")
            return False

        if result:
            self._logger.info("--> Reignition process: Reignition successful")
        else:
            self._logger.warning("--> Reignition process: Reignition unsuccessful")
            return False

        self._logger.info("--> Reignition process: Setting sputter pressure %s (mbar) in 10 seconds", sputter_pressure)
        self._timer.sleep(10)
        valve.set_pressure(sputter_pressure)

        self._logger.info("--> Reignition process: Checking plasma in 30 seconds...")
        self._timer.sleep(30)
        try:
            result = plasma_checker.check()
        except:
            self._logger.warning("Could not re-check plasma in reignition process")
            return False

        if result:
            self._logger.info("--> Reignition process: Reignition successful")
        else:
            self._logger.warning("--> Reignition process: Reignition unsuccessful")
            return False

    def _check_sequence(self, sequence):
        assert isinstance(sequence, list)

        for element in sequence:
            assert isinstance(element, (list, dict))


    def sputter_sequence(self, sequence, startpoint=0):
        self._check_sequence(sequence)

        self._julabo.on()
        iterations = len(sequence)

        for i in range(startpoint, iterations):
            self._logger.info("==> Sputter sequence: Starting sequence number %s of %s", i + 1, iterations)
            self._logger.info("==> Sputter sequence: with parameters --> %s", sequence[i])
            if isinstance(sequence[i], dict):
                self.sputter(**sequence[i])
            else:
                self.sputter(*sequence[i])
            self._logger.info("==> Sputter sequence: Finished sequence number %s of %s", i+ 1, iterations)
            self._logger.info("==> Sputter sequence: with parameters --> %s", sequence[i])

        self._julabo.off()
