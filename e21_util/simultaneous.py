import threading
from e21_util.interruptor import Interruptor, StopException

class StoppableThread(threading.Thread):
    def __init__(self, interruptor=None):
        super(StoppableThread, self).__init__()
        if interruptor is None:
            interruptor = Interruptor()

        if not isinstance(interruptor, Interruptor):
            raise RuntimeError("interruptor not an instance of Interruptor")

        self._interruptor = interruptor

    def run(self):
        while True:
            self._interruptor.stoppable()
            self.do_execute()

    def is_running(self):
        return not self._interruptor.is_stopped()

    def stop(self):
        self._interruptor.stop()

    def do_execute(self):
        pass