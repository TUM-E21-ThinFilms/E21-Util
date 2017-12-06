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


class Paths(object):
    GUN_CONFIG_PATH = "/home/sputter/Python/lib/config/gun.config"
    EMAIL_CONFIG_PATH = "/home/sputter/Python/lib/config/email.config"
    LOG_PATH = "/var/log/sputter/"
    RAMDISK = "/run/media/ramdisk"
    LOCK_DIR = RAMDISK
    HEIDENHAIN_LOCK_DIR = LOCK_DIR + "/heidenhain"
    CACHE_DIR = RAMDISK + "/cache/"
