import threading
import time
import datetime

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

    def sleep_til(self, timestamp, logger, interval=15):
        logger.info("Sleep until %s ...", datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'))
        while True:
            stoppable(self._interrupt)
            cur_time = time.time()
            if cur_time >= timestamp:
                break
            time.sleep(interval)
            logger.info("Current time: %s, goal: %s, diff in minutes %s", cur_time, timestamp, (timestamp - cur_time) / 60.0)

'''
    @:raises StopException
'''
def stoppable(interrupt):
    interrupt.stoppable()