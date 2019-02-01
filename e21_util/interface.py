# Copyright (C) 2017, see AUTHORS.md
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from e21_util.interruptor import Interruptor


class Loggable(object):
    def __init__(self, logger):
        self._logger = None
        self.set_logger(logger)

    def get_logger(self):
        return self._logger

    def set_logger(self, logger):
        if not isinstance(logger, logging.Logger) or logger is None:
            raise RuntimeError("Given logger must be an instance of logging.Logger")

        self._logger = logger


class Interruptable(object):
    def __init__(self, interrupter):
        self._interrupt = None
        self.set_interrupt(interrupter)

    def get_interrupt(self):
        return self._interrupt

    def set_interrupt(self, interrupt):
        if not isinstance(interrupt, Interruptor) or interrupt is None:
            raise RuntimeError("Given interrupt is not an instance of Interruptor")
        self._interrupt = interrupt

    def interrupt(self):
        self._interrupt.stop()
