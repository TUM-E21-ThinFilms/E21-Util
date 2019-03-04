import threading
import time
import datetime

from e21_util.timer import InterruptableTimer, AbstractTimer


class StopException(Exception):
    pass


class Interruptor(object):
    def __init__(self):
        self._event = threading.Event()

    def stop(self):
        self._event.set()

    def is_stopped(self):
        return self._event.is_set()

    def is_running(self):
        return not self._event.is_set()

    def stoppable(self):
        if self.is_stopped():
            raise StopException()


class InterruptableThread(threading.Thread):
    def __init__(self, interruptor):
        threading.Thread.__init__(self)
        self._interruptor = None
        self.set_interruptor(interruptor)

    def run(self):
        while self.is_running():
            self.do_execute()

    def is_running(self):
        return self._interruptor.is_running()

    def stop(self):
        self._interruptor.stop()

    def get_interruptor(self):
        return self._interruptor

    def set_interruptor(self, interruptor):
        assert isinstance(interruptor, Interruptor)
        self._interruptor = interruptor

    def do_execute(self):
        pass

    def stoppable(self):
        self._interruptor.stoppable()


class InterruptableTimerThread(InterruptableThread):
    def __init__(self, interruptor, timer):
        super(InterruptableTimerThread, self).__init__(interruptor)
        self._timer = None
        self.set_timer(timer)

    def set_timer(self, timer):
        assert isinstance(timer, AbstractTimer)
        self._timer = timer

    def set_interruptor(self, interruptor):
        super(InterruptableTimerThread, self).set_interruptor(interruptor)
        self._timer.set_interruptor(interruptor)


def stoppable(interrupt):
    '''
        @:raises StopException
    '''
    interrupt.stoppable()
