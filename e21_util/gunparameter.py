import ConfigParser

class GunConfig(object):
    def __init__(self):
        self._diff = 0
        self._tol = 0
        self._pos_1 = 0

    def get_tolerance(self):
        return self._tol

    def set_tolerance(self, value):
        self._tol = value

    def get_difference(self):
        return self._diff

    def set_difference(self, value):
        self._diff = value

    def get_absolute_gun_position(self):
        return self._pos_1

    def set_absolute_gun_position(self, pos):
        self._pos_1 = pos


class GunConfigParser(object):
    SECTION = 'GUN'

    def __init__(self, config_file):
        self._file = config_file

    def get_config(self):
        configparser = ConfigParser.RawConfigParser()
        configparser.read(self._file)

        config = GunConfig()
        config.set_tolerance(configparser.getint(self.SECTION, 'tolerance'))
        config.set_difference(configparser.getint(self.SECTION, 'gun_difference'))
        config.set_absolute_gun_position(configparser.getint(self.SECTION, 'gun_1'))
        return config

    def write_config(self, config):
        configparser = ConfigParser.RawConfigParser()
        configparser.add_section(self.SECTION)
        configparser.set(self.SECTION, 'tolerance', config.get_tolerance())
        configparser.set(self.SECTION, 'gun_difference', config.get_difference())
        configparser.set(self.SECTION, 'gun_1', config.get_absolute_gun_position())

        with open(self._file, 'wb') as file:
            configparser.write(file)
