import time
import datetime
import logging

from devcontroller.misc.thread import StoppableThread
from devcontroller.gun import GunController
from devcontroller.vat import VATController
from devcontroller.relay import RelaisController
from tpg26x.driver import PfeifferTPG26xDriver
from devcontroller.turbovat import TurboVATController
from devcontroller.turbo import TurboController


class Ventilation(object):
    def __init__(self, logger):
        self._logger = logger
        self._timer = time

        self._turbo, self._vat_ar, self._relais, self._turbovalve, self._gauge = None, None, None, None, None

    def drivers(self, turbo, turbovalve, relais, vat_ar, gauge):
        self._turbo, self._vat_ar, self._relais, self._turbovalve, self._gauge = turbo, vat_ar, relais, turbovalve, gauge

        self._check_drivers()

    def _check_drivers(self):
        assert isinstance(self._turbo, TurboController)
        assert isinstance(self._vat_ar, VATController)
        assert isinstance(self._relais, RelaisController)
        assert isinstance(self._turbovalve, TurboVATController)
        assert isinstance(self._gauge, PfeifferTPG26xDriver)  # TODO: might be changed to a GaugeController?

    def ventilate(self):
        try:
            self._logger.info("Ventilating the chamber...")
            self._logger.info("Waiting 5 seconds for user abortion...")
            self._timer.sleep(5)
            self._turbo.off()
            self._logger.info("Turbo is turning off.")
            self._logger.info("Closing turbo valve...")
            self._turbovalve.close()
            self._logger.info("Turbo valve closed")
            self._do_open_pfeiffer_pump()
            self._do_open_ar_valve()
            self._timer.sleep(15)

            self._do_turn_off_scroll()

            self._relais.scroll_off()
            self._relais.bypass_on()

            self._do_close_ar_valve()
            self._question("Is the bypass valve closed?", True)
            self._logger.info("Done. ")

        except:
            pass

    def _do_open_pfeiffer_pump(self):
        self._logger.info("Turning pfeiffer pump off...")
        self._question("Is the pfeiffer valve closed?", True)
        self._question("Is the pfeiffer pump turned off?", True)
        self._question("Is the hatch opened?", True)
        self._logger.info("Pfeiffer pump turned off.")

    def _do_turn_off_scroll(self):
        self._logger.info("Turning scroll off (if possible)")
        self._logger.info("Turbo at " + self._turbo.get_rotation_speed() + " rpm")
        self._logger.info("Turn off scroll if turbo has fully stopped!")
        self._question("Has the turbo pump stopped moving?", True)
        self._question("Is the scroll turned off?", True)
        self._question("Is the bypass valve opened?", True)

    def _do_close_ar_valve(self):
        self._question("Is the argon valve closed?", True)


    def _question(self, question, continue_with_yes=True):
        while True:
            response = raw_input(question + " (yes/no)")
            if continue_with_yes and response.lower() == "yes":
                self._logger.info(question + ". Answered with " + response)
                break
            if continue_with_yes == False and response.lower() == "no":
                self._logger.info(question + ". Answered with " + response)
                break

    def _do_open_ar_valve(self):
        self._question("Is the argon valve fully opened?", True)
        self._logger.info("Argon valve opened")

    def _do_turn_on_scroll(self):
        self._logger.info("Turning on scroll...")
        self._question("Is the scroll turned on?", True)
        self._question("Is the bypass valve open?", True)

    def _do_turn_on_pfeiffer(self):
        self._logger.info("Turning pfeiffer pump on")
        self._question("Can the hatch be opened?", False)
        self._question("Is the Pfeiffer valve opened?", True)
        self._question("Is the Pfeiffer pump turned on?", True)
        self._logger.info("Pfeiffer pump turned on.")

    def deventilate(self):
        try:
            self._logger.info("De-Ventilating the chamber...")
            self._logger.info("Waiting 5 seconds for user abortion...")
            self._timer.sleep(5)

            self._do_turn_on_scroll()
            self._do_turn_on_pfeiffer()
            self._logger.info("Waiting for pressure at 1.0e-1 mbar ...")
            self._wait_for_pressure(1.0e-1)
            self._do_turn_on_turbo()
            self._logger.info("Done. ")

        except:
            pass

    def _do_turn_on_turbo(self):
        self._question("Is the bypass valve closed?", True)
        self._question("Is the turbo valve opened?", True)
        self._question("Is the turbo pump on?", True)

    def _wait_for_pressure(self, pressure):
        while True:
            current_pressure = self._gauge.get_pressure_measurement()[1]
            self._logger.info("Current pressure: " + str(current_pressure)+" mbar")
            if current_pressure <= pressure:
                return

            self._timer.sleep(2)
