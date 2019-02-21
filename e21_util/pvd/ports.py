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

from e21_util.serialports import ConfigParser


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

    RASPBERRYPI_SERIAL = (2, 1)

    DEVICE_MKS_GAS_FLOW = MOXA_16_PORT_15
    DEVICE_RELAY = RASPBERRYPI_SERIAL
    DEVICE_CESAR = MOXA_16_PORT_13

    def __init__(self):
        pass

    def get_port(self, device):
        assert isinstance(device, tuple)
        assert 0 <= device[0] <= 2
        assert 0 <= device[1] <= 16

        if device == self.RASPBERRYPI_SERIAL:
            return "/dev/serial0"

        if device[0] == 0 or device[1] == 0:
            raise RuntimeError("Given device is currently not connected")

        if device[0] == 1:
            return "/dev/ttyUSB" + str(device[1] - 1)

        return ""
