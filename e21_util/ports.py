
class Ports(object):

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

    DEVICE_PFEIFFER_GAUGE    = MOXA_16_PORT_1
    DEVICE_JULABO            = MOXA_16_PORT_2
    DEVICE_RELAIS            = MOXA_16_PORT_3
    DEVICE_TURBO_VALVE       = MOXA_16_PORT_4
    DEVICE_LEAK_VALVE_AR     = MOXA_16_PORT_5
    DEVICE_LEAK_VALVE_O2     = MOXA_16_PORT_6
    DEVICE_MOTOR_Z           = MOXA_16_PORT_7
    DEVICE_MOTOR_X           = MOXA_16_PORT_8
    DEVICE_MOTOR_C           = MOXA_16_PORT_9
    DEVICE_MOTOR_D           = MOXA_16_PORT_10
    DEVICE_ADL_A             = MOXA_16_PORT_11
    DEVICE_TURBO_PUMP        = MOXA_16_PORT_12
    DEVICE_COMPRESSOR        = MOXA_16_PORT_13
    DEVICE_PHYTRON           = MOXA_16_PORT_14
    DEVICE_SPUTTER_TRUMPF_RF = MOXA_16_PORT_15
    DEVICE_SHUTTER           = MOXA_16_PORT_16

    DEVICE_HEATING           = MOXA_8_PORT_1
    DEVICE_ADL_B             = MOXA_8_PORT_2
    DEVICE_PFEIFFER_D21      = MOXA_8_PORT_3
    DEVICE_SPUTTER_TRUMPF_DC = MOXA_8_PORT_4


    def __init__(self):
        pass

    def get_port(self, device):
        assert isinstance(device, tuple)

        number = (device[0] - 1)*16 + (device[1])

        return "/dev/ttyUSB" + str(number)
