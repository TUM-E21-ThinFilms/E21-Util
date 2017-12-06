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

from e21_util.paths import Paths
from cachepy import *

class AbstractCache(object):
    def set(self, key, value):
        pass

    def get(self, key):
        pass

class AbstractCacheAdapter(object):
    def __init__(self, cache):
        self._cache = cache

    def set(self, func, value):
        chash = _hash(func, list(), self._cache.ttl, '')
        self._cache.backend.store_data(chash, value, '', self._cache.ttl)

    def get(self, func):
        chash = _hash(func, list(), self._cache.ttl, '')
        return self._cache.backend.get_data(chash, key='', ttl=self._cache.ttl)


CACHE_TRUMPFDC = AbstractCacheAdapter(Cache(Paths.CACHE_DIR + "trumpfdc.cache", ttl=2))