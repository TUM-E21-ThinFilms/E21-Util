import threading
from e21_util.interruptor import Interruptor

class StoppableThread(threading.Thread):
    def __init__(self, interruptor: Interruptor=Interruptor()):
        super(StoppableThread, self).__init__()
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