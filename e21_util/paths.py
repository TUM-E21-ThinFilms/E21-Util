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
    LOG_PATH = "/var/log/device/"
    RAMDISK = "/run/media/ramdisk"
    LOCK_DIR = "/run/lock"
    HEIDENHAIN_LOCK_DIR = LOCK_DIR + "/heidenhain"
    ENCODER_PATH = RAMDISK + "/encoder.save"
    ENCODER_LOCK_DIR = RAMDISK + "/encoder"
    CACHE_DIR = RAMDISK + "/cache/"

    CONFIG_PATH = '/etc/e21/'
    CONFIG_INSITU_PATH = CONFIG_PATH + 'in-situ/'

    SERIAL_PORT_PVD = CONFIG_PATH + 'pvd.yml'
    SERIAL_PORT_INSITU = CONFIG_PATH + 'insitu.yml'

