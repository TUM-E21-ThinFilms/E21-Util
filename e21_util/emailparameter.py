import ConfigParser


class EmailConfig(object):
    def __init__(self):
        self._port = 0
        self._user = ""
        self._host = ""
        self._password = ""

    def get_port(self):
        return self._port

    def get_user(self):
        return self._user

    def get_host(self):
        return self._host

    def get_password(self):
        return self._password

    def set_port(self, port):
        self._port = int(port)

    def set_user(self, user):
        self._user = str(user)

    def set_host(self, host):
        self._host = str(host)

    def set_password(self, password):
        self._password = str(password)


class EmailConfigParser(object):
    SECTION = 'EMAIL'

    DEFAULT_CONFIG_FILE = '/home/sputter/Python/lib/config/email.conf'

    def __init__(self, config_file=None):
        if config_file is None:
            config_file = self.DEFAULT_CONFIG_FILE

        self._file = config_file

    def get_config(self):
        configparser = ConfigParser.RawConfigParser()
        configparser.read(self._file)

        config = EmailConfig()
        config.set_port(configparser.getint(self.SECTION, 'port'))
        config.set_password(configparser.get(self.SECTION, 'password'))
        config.set_user(configparser.get(self.SECTION, 'user'))
        config.set_host(configparser.get(self.SECTION, 'host'))
        return config
