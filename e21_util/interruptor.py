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
    def __init__(self, interrupt, steps = 1):
        self._t = 0
        self._interrupt = interrupt
        if steps <= 0:
            raise RuntimeError("time steps must be positive")

        self._steps = steps

    def sleep(self, time_sec):
        while time_sec > self._steps:
            self._interrupt.stoppable()
            time.sleep(self._steps)
            time_sec -= self._steps

        time.sleep(time_sec)
        self._interrupt.stoppable()

'''
    @:raises StopException
'''
def stoppable(interrupt):
    interrupt.stoppable()