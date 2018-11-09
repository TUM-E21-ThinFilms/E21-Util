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

    DEVICE_MKS_GAS_FLOW = MOXA_16_PORT_15

    def __init__(self):
        pass

    def get_port(self, device):
        assert isinstance(device, tuple)
        assert 0 <= device[0] <= 1
        assert 0 <= device[1] <= 16

        if device[0] == 0 or device[1] == 0:
            raise RuntimeError("Given device is currently not connected")

        if device[0] == 1:
            return "/dev/ttyUSB" + str(device[1] + 1)

        return ""
