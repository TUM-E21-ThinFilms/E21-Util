import threading

class Simultaneous(object):
    def __init__(self):
        self._threads = []
        self._started = False

    def add(self, function, *arguments):
        if self._started:
            raise RuntimeError("Cannot add threads to an already running scheduler")

        thread = threading.Thread(target=function, args=arguments)
        self._threads.append(thread)

    def run(self):
        self._started = True

        for thread in self._threads:
            thread.start()

    def join(self):
        if not self._started:
            raise RuntimeError("Scheduler not started yet")

        for thread in self._threads:
            thread.join()