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

from e21_util.serialports import AbstractSerialFactory, ConfigParser
from e21_util.serial_connection import AbstractTransport
from e21_util.ports import AbstractPorts
from e21_util.serialports import MoxaConnection, MappingConnection, NotConnectedConnection
from e21_util.paths import Paths


class Connection(AbstractPorts):

    def get_default_factory(self):
        return SerialFactory(ConfigParser(Paths.SERIAL_PORT_PVD))


class SerialFactory(AbstractSerialFactory):
    CONNECTION_MOXA = 'Moxa'

    OFFSET_MOXA = 0

    def __init__(self, config_parser):
        super(SerialFactory, self).__init__(config_parser)

        self._moxa = MoxaConnection(config_parser.get_connection(self.CONNECTION_MOXA), self.OFFSET_MOXA)
        self._nc = NotConnectedConnection()

    def get_path(self, name):
        connection = self._parser.get_connection_for_device(name)
        con_name = connection[ConfigParser.KEY_NAME]

        if con_name == self.CONNECTION_MOXA:
            return self._moxa.get_port(name)
        elif con_name == self.CONNECTION_NOT_CONNECTED:
            return self._nc.get_port(name)
        else:
            raise RuntimeError("Unknown connection {} specified for device {}".format(con_name, name))
