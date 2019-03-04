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


from serial.serialutil import SerialTimeoutException
from e21_util.lock import InterProcessTransportLock

try:
    import serial
    class AbstractSerial(serial.Serial):
        pass
except:
    import serial.serialposix
    class AbstractSerial(serial.serialposix.Serial):
        pass

class AbstractTransport(object):
    def read_until(self, delimiter):
        raise NotImplementedError()

    def read_bytes(self, num_bytes):
        raise NotImplementedError()

    def read(self, num_bytes):
        # Returns bytearray
        raise NotImplementedError()

    def write(self, data, encoding='ascii'):
        raise NotImplementedError()


class Serial(AbstractSerial, AbstractTransport):
    def __init__(self, *args, **kwargs):
        super(Serial, self).__init__(*args, **kwargs)
        self._buffer = bytearray()
        self._max_bytes = 1
        self._lock = InterProcessTransportLock(self)

    def set_lock(self, lock):
        self._lock = lock

    def get_lock(self):
        return self._lock

    def __enter__(self):
        super(Serial, self).__enter__()
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # do not call super __exit__, the serial connection should not be closed
        self._lock.release()

    def get_device(self):
        return self._port

    def write(self, data, encoding='ascii'):

        msg = data

        if isinstance(data, str):
            msg = bytearray(data, encoding)
        elif isinstance(data, bytearray):
            pass
        elif isinstance(data, byte):
            pass
        else:
            raise RuntimeError("Unknown data given")

        return super(Serial, self).write(msg)

    def read(self, num_bytes):
        data = super(Serial, self).read(num_bytes)
        if len(data) == 0:
            raise SerialTimeoutException()
        return data

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
