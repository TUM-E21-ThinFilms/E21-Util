# Copyright (C) 2018, see AUTHORS.md
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

import serial


class Serial(serial.Serial):
    def __init__(self, *args, **kwargs):
        super(Serial, self).__init__(*args, **kwargs)
        self._name = ""
        self._buffer = bytearray()
        self._max_bytes = 32

    def set_name(self, name):
        self._name = name  # TODO

    def get_name(self):
        return self._name

    def write(self, data, encoding='ascii'):

        msg = data

        if isinstance(data, str):
            msg = bytearray(data, encoding)
        elif isinstance(data, bytearray):
            msg = data
        else:
            raise RuntimeError("Unknown data given")

        return super(Serial, self).write(msg)

    def read(self, num_bytes):
        return super(Serial, self).read(num_bytes)

    def read_bytes(self, num_bytes):

        buffer_size = len(self._buffer)
        if buffer_size > num_bytes:
            data, self._buffer = self._buffer[:num_bytes], self._buffer[num_bytes:]
        elif 0 < buffer_size <= num_bytes:
            data, self._buffer = self._buffer, bytearray()
        else:
            self._buffer += self.read(num_bytes)
            return self.read_bytes(num_bytes)

        return data

    def read_until(self, delimiter):
        if delimiter in self._buffer:
            data, delimiter, self._buffer = self._buffer.partition(delimiter)
            return data + delimiter
        else:
            self._buffer += self.read(self._max_bytes)
            return self.read_until(delimiter)
