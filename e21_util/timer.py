#  Copyright (C) 2019, see AUTHORS.md
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


class AbstractTimer(object):
    def sleep(self, time_sec):
        raise NotImplementedError()

    def sleep_until(self, time_sec):
        raise NotImplementedError()


class InterruptableTimer(AbstractTimer):
    def __init__(self, interrupt, steps=1):
        self._t = 0
        self._interrupt = interrupt
        if steps <= 0:
            raise RuntimeError("time steps must be positive")

        self._steps = steps

    def set_interruptor(self, interruptor):
        self._interrupt = interruptor

    def sleep(self, time_sec):
        while time_sec > self._steps:
            self._interrupt.stoppable()
            time.sleep(self._steps)
            time_sec -= self._steps

        time.sleep(time_sec)
        self._interrupt.stoppable()

    def sleep_until(self, timestamp, logger, interval=15):
        logger.info("Sleep until %s ...", datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'))
        while True:
            self._interrupt.stoppable()
            cur_time = time.time()
            if cur_time >= timestamp:
                break
            time.sleep(interval)
            logger.info("Current time: %s, goal: %s, diff in minutes %s", cur_time, timestamp,
                        (timestamp - cur_time) / 60.0)


class DummyTimer(object):
    def sleep(self, time_sec):
        pass

    def sleep_until(self):
        pass
