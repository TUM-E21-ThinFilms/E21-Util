import time
from functools import wraps
from e21_util.interface import Loggable, Interruptable

def retry(retry_count=3, logger=None, catch=Exception, interruptor=None, delay=0):
    def retry_decorator(f):
        @wraps(f)
        def wrapped(self, *f_args, **f_kwargs):
            if logger is None and isinstance(self, Loggable):
                loc_logger = self.get_logger()
            else:
                loc_logger = logger

            if interruptor is True and isinstance(self, Interruptable):
                loc_interruptor = self.get_interrupt()
            else:
                loc_interruptor = interruptor
            i = 0
            while i < retry_count - 1:
                if not loc_interruptor is None:
                    loc_interruptor.stoppable()
                i += 1
                try:
                    return f(self, *f_args, **f_kwargs)
                except catch as e:
                    if not loc_logger is None:
                        loc_logger.warning("Catched exception in retry clause. Retry (%s) of (%s)", i, retry_count)
                        loc_logger.exception(e)
                    time.sleep(delay)

            return f(self, *f_args, **f_kwargs)

        return wrapped

    return retry_decorator