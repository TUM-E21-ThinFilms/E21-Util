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


class GunSelectionConfig(object):
    def __init__(self):
        self.gun_sputter = []
        self.gun_target = []
        self.gun_number = 0

    def get_gun_sputter(self, gun_number):
        self._validate_gun_number(gun_number)
        return self.gun_sputter[gun_number]

    def set_gun_sputter(self, gun_number, sputter):
        self._validate_gun_number(gun_number)
        self.gun_sputter[gun_number] = sputter

    def get_gun_target(self, gun_number):
        self._validate_gun_number(gun_number)
        return self.gun_target[gun_number]

    def set_gun_target(self, gun_number, target):
        self._validate_gun_number(gun_number)
        self.gun_target[gun_number] = target

    def _validate_gun_number(self, gun_number):
        if not isinstance(gun_number, (int, long)):
            raise ValueError("gun number must be an interger")

        if gun_number <= 0 or gun_number > self.gun_number:
            raise ValueError("gun number must be between 1 and " + str(self.gun_number))

    def get_gun_number(self):
        return self.gun_number

    def set_gun_number(self, number):
        self.gun_number = number
        self.gun_sputter = number*[0]
        self.gun_target = number*[""]


class GunSelectionConfigParser(object):
    SECTION = 'GUN_SELECTION'

    def __init__(self, config_file):
        self._file = config_file

    def get_config(self):
        configparser = ConfigParser.RawConfigParser()
        configparser.read(self._file)

        config = GunSelectionConfig()
        config.set_gun_number(configparser.getint(self.SECTION, 'gun_number'))

        for i in range(1, config.get_gun_number()):
            config.set_gun_sputter(i, configparser.getint(self.SECTION, 'gun_' + i + '_sputter'))
            config.set_gun_target(i, configparser.get(self.SECTION, 'gun_' + i + '_target'))

        return config

    def write_config(self, config):
        configparser = ConfigParser.RawConfigParser()
        configparser.add_section(self.SECTION)

        for i in range(1, config.get_gun_number()):
            configparser.set(self.SECTION, 'gun_' + i + '_sputter', config.get_gun_sputter(i))
            configparser.set(self.SECTION, 'gun_' + i + '_target', config.get_gun_target(i))

        with open(self._file, 'wb') as file:
            configparser.write(file)
