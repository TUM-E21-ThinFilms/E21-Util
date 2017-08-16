import threading
import time

class StopException(Exception):
    pass

class Interruptor(object):
    def __init__(self):
        self._event = threading.Event()

    def stop(self):
        self._event.set()

    def is_stopped(self):
        return self._event.is_set()

    def stoppable(self):
        if self.is_stopped():
            raise StopException()

class InterruptableTimer(object):
    def __init__(self, interrupt):
        self._t = 0
        self._interrupt = interrupt

    def sleep(self, time_sec):
        while time_sec > 1:
            self._interrupt.stoppable()
            time.sleep(1)
            time_sec -= 1

        time.sleep(time_sec)
        self._interrupt.stoppable()

'''
    @:raises StopException
'''
def stoppable(interrupt):
    interrupt.stoppable()