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

import fasteners

LOCK_DIR = "/run/media/ramdisk"

def HEIDENHAIN_LOCK():
    return fasteners.InterProcessLock(LOCK_DIR + "/heidenhain")

class InterProcessTransportLock(fasteners.InterProcessLock):
    def __init__(self, transport, *args, **kwargs):
        super(InterProcessTransportLock, self).__init__(LOCK_DIR + transport.get_name(), *args, **kwargs)

