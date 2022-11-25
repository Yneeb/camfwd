# Copyright (C) 2022 Douglas Button

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.

# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <https://www.gnu.org/licenses/>.

from PIL.Image import open as image_open
from PIL.ImageStat import Stat as image_stat
from io import BytesIO


def image_from_bytes(data):
    with BytesIO(data) as image_data:
        img = image_open(image_data)
        img.load()
        return img


def get_contrast(image):
    return image_stat(image.convert("L")).stddev[0]


def get_entropy(image):
    return image.entropy()
