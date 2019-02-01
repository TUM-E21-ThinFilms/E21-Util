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

import yaml
import serial
import serial.serialutil as serialutil

from e21_util.serial_connection import Serial


class ParseError(RuntimeError):
    pass


class ConfigParser(object):
    KEY_NAME = 'Name'
    KEY_DEVICES = 'Devices'
    KEY_BAUDRATE = 'Baudrate'
    KEY_PARITY = 'Parity'
    KEY_DATABITS = 'Databits'
    KEY_STOPBITS = 'Stopbits'
    KEY_TIMEOUT = 'Timeout'

    KEY_CONNECTION = 'Connections'
    KEY_PORTS = 'Ports'
    KEY_TYPE = 'Type'

    DEFAULT_DEVICE = {
        KEY_NAME: None,
        KEY_BAUDRATE: None,
        KEY_PARITY: None,
        KEY_STOPBITS: 1,
        KEY_DATABITS: None,
        KEY_TIMEOUT: 1,
        KEY_CONNECTION: None,
    }

    DEFAULT_CONNECTION = {
        KEY_NAME: None,
        KEY_TYPE: None,
        KEY_DEVICES: []
    }

    CONNECTION_TYPE_NOT_CONNECTED = 'Not Connected'
    CONNECTION_TYPE_USB2RS232 = 'USB'
    CONNECTION_TYPE_MAPPING = 'Mapping'
    CONNECTION_TYPE_MOXA16 = 'Moxa-16'
    CONNECTION_TYPE_MOXA8 = 'Moxa-8'

    KEY_CONNECTION_DEVICE_MAPPING = 'Mapping'

    MAPPING_PARITY = {
        'Odd': serialutil.PARITY_ODD,
        'O': serialutil.PARITY_ODD,
        '': serialutil.PARITY_NONE,
        'None': serialutil.PARITY_NONE,
        'N': serialutil.PARITY_NONE,
        'Even': serialutil.PARITY_EVEN,
        'E': serialutil.PARITY_EVEN,
        'Mark': serialutil.PARITY_MARK,
        'M': serialutil.PARITY_MARK,
        'S': serialutil.PARITY_SPACE,
        'Space': serialutil.PARITY_SPACE
    }

    MAPPING_STOPBIT = {
        'One': serialutil.STOPBITS_ONE,
        '1': serialutil.STOPBITS_ONE,
        'Two': serialutil.STOPBITS_TWO,
        '2': serialutil.STOPBITS_TWO,
        '1.5': serialutil.STOPBITS_ONE_POINT_FIVE,
    }

    MAPPING_DATABITS = {
        '5': serialutil.FIVEBITS,
        'Five': serialutil.FIVEBITS,
        '6': serialutil.SIXBITS,
        'Six': serialutil.SIXBITS,
        '7': serialutil.SEVENBITS,
        'Seven': serialutil.SEVENBITS,
        '8': serialutil.EIGHTBITS,
        'Eight': serialutil.EIGHTBITS
    }

    def __init__(self, file):
        self._file = file
        self._devices = []
        self._connections = []
        self._has_parsed = False

    def parse(self):
        with open(self._file, 'r') as stream:
            config = yaml.load(stream)

        self._devices = self._parse_devices(config)
        self._connections = self._parse_connections(config)

        # Now attach for every device a connection. We can check at the same time, that every device has exactly ONE
        # connection.
        self._connect_devices()

        self._has_parsed = True

    def has_parsed(self):
        return self._has_parsed

    def _connect_devices(self):
        for dev in self._devices:
            name = dev[self.KEY_NAME]
            connections = self._search_connection(name)

            if len(connections) > 1:
                con_names = list(map(lambda x: x[self.KEY_NAME], connections))
                raise ParseError("The device '{}' has multiple connection definitions: {}".format(name, con_names))
            elif len(connections) == 0:
                raise ParseError("The device '{}' has no connection definition".format(name))

            dev[self.KEY_CONNECTION] = connections[0][self.KEY_NAME]

    def _search_connection(self, name):
        found = []

        for connection in self._connections:
            devices = connection[self.KEY_DEVICES]
            if name in devices:
                found.append(connection)

        return found

    def get_key(self, key, dicts, default=None, raise_exception=True):
        if not isinstance(dicts, list):
            dicts = [dicts]

        for dict in dicts:
            if dict is None:
                continue

            if key in dict:
                return dict[key]

        if raise_exception:
            raise ParseError("The key {} does not exit in the config file".format(key))
        else:
            return default

    def _parse_devices(self, config):
        devices = self.get_key(self.KEY_DEVICES, config)

        dev = []

        for device in devices:
            if device is None:
                continue

            device_name, device_properties = device.popitem()
            dev.append(self._parse_device(device_name, device_properties))

        return dev

    def _check_mapping(self, key, mapping):
        if key is None:
            return

        if key not in mapping.keys():
            raise ParseError('Unknown key {} found'.format(key))

        return mapping[key]

    def _set_device(self, device, key, value):
        if value is None:
            return

        device[key] = value

    def _parse_device(self, device_name, device_properties):

        # Parse the options
        # these are required
        try:
            baudrate = self.get_key(self.KEY_BAUDRATE, device_properties)
            databits = str(self.get_key(self.KEY_DATABITS, device_properties))
            parity = str(self.get_key(self.KEY_PARITY, device_properties))

            # stopbits and timeout are not so important, stopbits is usually 1, and timeout can be set to 1 sec
            stopbits = str(self.get_key(self.KEY_STOPBITS, device_properties, raise_exception=False))
            timeout = self.get_key(self.KEY_TIMEOUT, device_properties, default=self.DEFAULT_DEVICE[self.KEY_TIMEOUT],
                                   raise_exception=False)
        except ParseError as e:
            raise ParseError("Exception while parsing device {}".format(device_name), e)

        # Validate the options
        if timeout is "None":
            timeout = None
        else:
            try:
                timeout = float(timeout)
            except ValueError:
                raise ParseError("Could not parse timeout '{}' to float for device {}".format(timeout, device_name))

        if baudrate not in serialutil.SerialBase.BAUDRATES:
            raise ParseError("Unknown baudrate {} found for device {}".format(baudrate, device_name))

        databits = self._check_mapping(databits, self.MAPPING_DATABITS)
        parity = self._check_mapping(parity, self.MAPPING_PARITY)
        stopbits = self._check_mapping(stopbits, self.MAPPING_STOPBIT)

        # Create a new device with the given options
        device = self.DEFAULT_DEVICE.copy()
        self._set_device(device, self.KEY_NAME, device_name)
        self._set_device(device, self.KEY_BAUDRATE, baudrate)
        self._set_device(device, self.KEY_DATABITS, databits)
        self._set_device(device, self.KEY_PARITY, parity)
        self._set_device(device, self.KEY_STOPBITS, stopbits)
        # Note that we cant use the method _set_device, since timeout can be None, and this has a special meaning
        # for the serial connection (wait forever).
        device[self.KEY_TIMEOUT] = timeout

        return device

    def _parse_connections(self, config):
        connections = self.get_key(self.KEY_CONNECTION, config)

        conns = []

        for connection in connections:
            if connection is None:
                continue

            connection_name, connection_options = connection.popitem()
            conns.append(self._parse_connection(connection_name, connection_options))

        return conns

    def _parse_connection(self, name, options):
        con_type = self.get_key(self.KEY_TYPE, options)

        if con_type == self.CONNECTION_TYPE_NOT_CONNECTED:
            con = self._parse_connection_not_connected(options)
        elif con_type == self.CONNECTION_TYPE_MAPPING:
            con = self._parse_connection_mapping(options)
        elif con_type == self.CONNECTION_TYPE_MOXA16:
            con = self._parse_connection_moxa(options, name, max_ports=16)
        elif con_type == self.CONNECTION_TYPE_MOXA8:
            con = self._parse_connection_moxa(options, name, max_ports=8)
        elif con_type == self.CONNECTION_TYPE_USB2RS232:
            con = self._parse_connection_usb2rs232(options)
        else:
            raise ParseError("Unknown connection type '{}' found".format(type))

        con[self.KEY_NAME] = name
        con[self.KEY_TYPE] = con_type

        return con

    def _parse_connection_not_connected(self, options):
        ports = self.get_key(self.KEY_PORTS, options, default=[], raise_exception=False)

        devices = []
        # We dont care about the port number, since they are all not connected ;)
        for entry in ports:
            id, dev = entry.popitem()
            devices.append(dev)

        connection = self.DEFAULT_CONNECTION.copy()
        connection[self.KEY_DEVICES] = devices

        return connection

    def _parse_connection_mapping(self, options):
        ports = self.get_key(self.KEY_PORTS, options)

        devices = []
        mapping = []

        for entry in ports:
            if entry is None:
                continue

            port, dev = entry.popitem()
            devices.append(dev)
            # Mapping: port id -> index: device
            # Note, since we're adding the devices from an empty list,
            # the index of dev in devices is just len(devices) - 1
            # alternatively, use devices.index(dev)
            mapping.append((len(devices) - 1, port))

        connection = self.DEFAULT_CONNECTION.copy()
        connection[self.KEY_DEVICES] = devices
        connection[self.KEY_CONNECTION_DEVICE_MAPPING] = mapping

        return connection

    def _parse_connection_moxa(self, options, name, max_ports=16):
        # We need the parameter name, just for easier error finding,
        # otherwise there is not necessity for it.

        con = self._parse_connection_mapping(options)
        ports = con[self.KEY_DEVICES]

        if len(ports) > max_ports:
            raise ParseError(
                "The moxa device {} supports only {} ports, but there are {} devices".format(name, max_ports,
                                                                                             len(ports)))

        return con

    def _parse_connection_usb2rs232(self, options):
        # maybe there will come something in the future ...
        return self._parse_connection_mapping(options)

    def get_device(self, name):
        for dev in self._devices:
            if dev[self.KEY_NAME] == name:
                return dev

        raise RuntimeError("No definition found for device '{}'".format(name))

    def get_connection(self, name):
        for con in self._connections:
            if con[self.KEY_NAME] == name:
                return con

        raise RuntimeError("No definition found for connection '{}'".format(name))

    def get_connection_for_device(self, name):
        return self.get_connection(self.get_device(name)[self.KEY_CONNECTION])


class MappingConnection(object):
    def __init__(self, config):
        self._config = config

    def _map_name_to_port_index(self, name):

        dev_index = None

        for index, dev in enumerate(self._config[ConfigParser.KEY_DEVICES]):
            if dev == name:
                dev_index = index

        if dev_index is None:
            raise RuntimeError("Could not find a port for device '{}' in connection '{}'".format(name, self._config[
                ConfigParser.KEY_NAME]))

        for mapping in self._config[ConfigParser.KEY_CONNECTION_DEVICE_MAPPING]:
            if mapping[0] == dev_index:
                return int(mapping[1])

        # This is in principle not going to happen
        raise RuntimeError("No mapping definition found for device '{}' in connection '{}'".format(name, self._config[
            ConfigParser.KEY_NAME]))

    def get_port(self, name):
        return self._map_name_to_port_index(name)


class MoxaConnection(MappingConnection):
    def __init__(self, config, offset):
        assert config[ConfigParser.KEY_TYPE] in [ConfigParser.CONNECTION_TYPE_MOXA8,
                                                 ConfigParser.CONNECTION_TYPE_MOXA16]

        super(MoxaConnection, self).__init__(config)

        self._offset = offset

    def get_port(self, name):
        # For moxa devices we subtract 1 since the user starts counting with 1, whereas computers start counting with 0
        physical_port_number = self._map_name_to_port_index(name) - 1 + self._offset

        return "/dev/ttyUSB{}".format(physical_port_number)


class USBToRS232Connection(MappingConnection):
    def __init__(self, config):
        assert config[ConfigParser.KEY_TYPE] == ConfigParser.CONNECTION_TYPE_USB2RS232
        super(USBToRS232Connection, self).__init__(config)

    def get_port(self, name):
        physical_port_number = self._map_name_to_port_index(name)

        return "/dev/ttyUSB{}".format(physical_port_number)


class SimpleConnection(object):
    def __init__(self, config):
        assert config[ConfigParser.KEY_TYPE] == ConfigParser.CONNECTION_TYPE_DIRECT
        self._config = config

    def get_port(self, name):
        pass


class NotConnectedConnection(object):
    def get_port(self, name):
        raise RuntimeError("The device {} is not connected".format(name))


class AbstractSerialFactory(object):
    def __init__(self, config_parser):
        assert isinstance(config_parser, ConfigParser)

        self._parser = config_parser
        if not self._parser.has_parsed():
            self._parser.parse()

    def get_path(self, name):
        raise NotImplementedError()

    def get_transport(self, name):
        config = self._parser.get_device(name)

        path = self.get_path(name)

        return Serial(path, config[ConfigParser.KEY_BAUDRATE], int(config[ConfigParser.KEY_DATABITS]),
                      config[ConfigParser.KEY_PARITY], config[ConfigParser.KEY_STOPBITS],
                      config[ConfigParser.KEY_TIMEOUT])


class BigChamberRPiSerialFactory(AbstractSerialFactory):
    CONNECTION_MAPPING = 'Mapping'

    def __init__(self, config_parser):
        super(BigChamberRPiSerialFactory, self).__init__(config_parser)

        self._mapping = MappingConnection(config_parser.get_connection(self.CONNECTION_MAPPING))
        self._nc = NotConnectedConnection()

    def get_path(self, name):
        connection = self._parser.get_connection_for_device(name)
        con_name = connection[ConfigParser.KEY_NAME]

        if con_name == self.CONNECTION_MAPPING:
            return self._moxa.get_port(name)
        elif con_name == self.CONNECTION_NOT_CONNECTED:
            return self._nc.get_port(name)
        else:
            raise RuntimeError("Unknown connection {} specified for device {}".format(con_name, name))
