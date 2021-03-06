# Copyright (C) 2018, see AUTHORS.md
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from e21_util.serialports import AbstractSerialFactory


class AbstractPorts(object):
    def __init__(self, factory=None):
        if factory is None:
            factory = self.get_default_factory()

        assert isinstance(factory, AbstractSerialFactory)

        self._factory = factory

    def get_default_factory(self):
        return None

    def get_transport(self, name):
        return self._factory.get_transport(name)


class Ports(object):
    NOT_CONNECTED = (0, 0)

    MOXA_16_PORT_1 = (1, 1)
    MOXA_16_PORT_2 = (1, 2)
    MOXA_16_PORT_3 = (1, 3)
    MOXA_16_PORT_4 = (1, 4)
    MOXA_16_PORT_5 = (1, 5)
    MOXA_16_PORT_6 = (1, 6)
    MOXA_16_PORT_7 = (1, 7)
    MOXA_16_PORT_8 = (1, 8)
    MOXA_16_PORT_9 = (1, 9)
    MOXA_16_PORT_10 = (1, 10)
    MOXA_16_PORT_11 = (1, 11)
    MOXA_16_PORT_12 = (1, 12)
    MOXA_16_PORT_13 = (1, 13)
    MOXA_16_PORT_14 = (1, 14)
    MOXA_16_PORT_15 = (1, 15)
    MOXA_16_PORT_16 = (1, 16)

    MOXA_8_PORT_1 = (2, 1)
    MOXA_8_PORT_2 = (2, 2)
    MOXA_8_PORT_3 = (2, 3)
    MOXA_8_PORT_4 = (2, 4)
    MOXA_8_PORT_5 = (2, 5)
    MOXA_8_PORT_6 = (2, 6)
    MOXA_8_PORT_7 = (2, 7)
    MOXA_8_PORT_8 = (2, 8)

    USB_TO_RS232_1 = (3, 1)
    USB_TO_RS232_2 = (3, 2)

    # DEVICE_TERRANOVA = MOXA_16_PORT_1
    # DEVICE_RELAY = MOXA_16_PORT_2
    # DEVICE_PHYTRON = MOXA_16_PORT_3
    DEVICE_PFEIFFER_GAUGE = MOXA_16_PORT_4
    DEVICE_TURBO_VALVE = MOXA_16_PORT_5
    DEVICE_MOTOR_Z = MOXA_16_PORT_6
    DEVICE_MOTOR_X = MOXA_16_PORT_7
    DEVICE_MOTOR_C = MOXA_16_PORT_8
    DEVICE_MOTOR_D = NOT_CONNECTED
    DEVICE_GAUGE_CRYO = MOXA_16_PORT_10
    DEVICE_COMPRESSOR = MOXA_16_PORT_11
    DEVICE_LEAK_VALVE_O2 = MOXA_16_PORT_12
    DEVICE_TURBO_PUMP = MOXA_16_PORT_13
    DEVICE_LEAK_VALVE_AR = MOXA_16_PORT_14
    DEVICE_JULABO = MOXA_16_PORT_15
    DEVICE_SHUTTER = MOXA_16_PORT_16

    DEVICE_EDWARDS_NXDS = MOXA_8_PORT_8

    DEVICE_ADL_B = MOXA_8_PORT_2
    DEVICE_PFEIFFER_TURBO = MOXA_8_PORT_3
    DEVICE_SPUTTER_TRUMPF_DC = MOXA_8_PORT_4
    DEVICE_ADL_A = MOXA_8_PORT_5
    DEVICE_SPUTTER_TRUMPF_RF = MOXA_8_PORT_6
    DEVICE_HEATING = MOXA_8_PORT_7

    DEVICE_LAKESHORE = USB_TO_RS232_1
    DEVICE_VOLTCRAFT_IR_1200 = USB_TO_RS232_2

    def __init__(self):
        pass

    def get_port(self, device):
        assert isinstance(device, tuple)
        assert 0 <= device[0] <= 3
        assert 0 <= device[1] <= 16

        if device[0] == 2 and device[1] > 8:
            raise RuntimeError("Moxa-Box 8 has only 8 ports. Cannot assign port " + str(device[1]))

        if device[0] == 0 or device[1] == 0:
            raise RuntimeError("Given device is currently not connected")

        if device[0] == 3:
            if device[1] == 1:
                return "/dev/ttyUSB0"
            if device[1] == 2:
                return "/dev/ttyUSB25"

            raise RuntimeError("Only one USB to RS232 connection available")

        number = (device[0] - 1) * 16 + (device[1])

        return "/dev/ttyUSB" + str(number)


class BigChamberRPiPorts(AbstractPorts):
    DEVICE_RELAY = 'Relay'

    def get_default_factory(self):
        return BigChamberRPiSerialFactory(ConfigParser('e21_util/config/rpi.yml'))
