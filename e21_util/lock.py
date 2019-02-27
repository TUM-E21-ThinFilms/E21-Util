# Copyright (C) 2016, see AUTHORS.md
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

import os
import fasteners
from e21_util.paths import Paths

LOCK_DIR = Paths.LOCK_DIR
HEIDENHAIN_LOCK_DIR = Paths.HEIDENHAIN_LOCK_DIR
ENCODER_LOCK_DIR = Paths.ENCODER_LOCK_DIR

def HEIDENHAIN_LOCK():
    return fasteners.InterProcessLock(HEIDENHAIN_LOCK_DIR)

def ENCODER_FILE_LOCK():
    return fasteners.InterProcessLock(ENCODER_LOCK_DIR)

class InterProcessTransportLock(fasteners.InterProcessLock):
    def __init__(self, transport, *args, **kwargs):
        # according to http://www.pathname.com/fhs/pub/fhs-2.3.html#VARLOCKLOCKFILES
        # lock files should be saved as
        # /run/lock/LCK..ttyUSBxx
        lock_file = LOCK_DIR + "LCK.." + os.path.basename(transport.get_device())
        super(InterProcessTransportLock, self).__init__(lock_file, *args, **kwargs)

