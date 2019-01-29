class AbstractPorts(object):
    def __init__(self, factory=None):
        if factory is None:
            factory = self.get_default_factory()

        assert isinstance(factory, SerialFactory)

        self._factory = factory

    def get_default_factory(self):
        return None

    def get_transport(self, name):
        return self._factory.get_transport(name)