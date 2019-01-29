# Copyright (C) 2019, see AUTHORS.md
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

from e21_util.serialports import SerialFactory
from e21_util.serial_connection import AbstractTransport
from e21_util.port.ports import AbstractPorts


class Ports(AbstractPorts):
    DEVICE_TERRANOVA = 'Terranova'

    def get_default_factory(self):
        return SerialFactory(ConfigParser('e21_util/config/insitu.yml'))


class SerialFactory(SerialFactory):
    CONNECTION_MOXA_16 = 'Moxa 1'
    CONNECTION_MOXA_8 = 'Moxa 2'
    CONNECTION_NOT_CONNECTED = 'Not Connected'
    CONNECTION_USB_2_RS232 = 'USB to RS232'

    OFFSET_MOXA_16 = 1
    OFFSET_MOXA_8 = 17

    def __init__(self, config_parser):
        super(SerialFactory, self).__init__(config_parser)

        self._moxa16 = MoxaConnection(config_parser.get_connection(self.CONNECTION_MOXA_16), self.OFFSET_MOXA_16)
        self._moxa8 = MoxaConnection(config_parser.get_connection(self.CONNECTION_MOXA_8), self.OFFSET_MOXA_8)
        self._usb = USBToRS232Connection(config_parser.get_connection(self.CONNECTION_USB_2_RS232))
        self._nc = NotConnectedConnection()

    def get_path(self, name):
        connection = self._parser.get_connection_for_device(name)
        con_name = connection[ConfigParser.KEY_NAME]

        if con_name == self.CONNECTION_MOXA_16:
            return self._moxa16.get_port(name)
        elif con_name == self.CONNECTION_MOXA_8:
            return self._moxa8.get_port(name)
        elif con_name == self.CONNECTION_USB_2_RS232:
            return self._usb.get_port(name)
        elif con_name == self.CONNECTION_NOT_CONNECTED:
            return self._nc.get_port(name)
        else:
            raise RuntimeError("Unknown connection {} specified for device {}".format(con_name, name))
