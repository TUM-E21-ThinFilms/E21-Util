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
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

CACHE_TRUMPFDC_NAMESPACE = 'trumpfdc'
CACHE_TRUMPFDC_EXPIRE = 2

CACHE_OPTIONS = {
    'cache.type':              'file',
    'cache.data_dir':          Paths.CACHE_DIR,
    'cache.lock_dir':          Paths.LOCK_DIR,
    'cache.regions':           ", ".join([CACHE_TRUMPFDC_NAMESPACE]),
    'cache.short_term.type':   'file',
    'cache.short_term.expire': CACHE_TRUMPFDC_EXPIRE
}

CACHE = CacheManager(**parse_cache_config_options(CACHE_OPTIONS))

CACHE_TRUMPFDC = CACHE.region(CACHE_TRUMPFDC_NAMESPACE)