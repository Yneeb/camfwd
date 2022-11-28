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

from camfwd.analysis import get_contrast, get_entropy, image_from_bytes
from PIL import UnidentifiedImageError
from PIL.Image import frombytes as create_image, Image
from unittest import TestCase
from base64 import b64decode

TEST_IMAGE = create_image("RGB", (2, 2), (
    b"\x52\x84\x91" b"\x34\x54\x5b"
    b"\x08\x10\x6b" b"\x02\xf9\x09"
))
TEST_JPG = b64decode(
    b"/9j/4AAQSkZJRgABAQEBLAEsAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEB"
    b"AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEB"
    b"AQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wgAR"
    b"CAABAAEDAREAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAACP/EABUBAQEAAAAAAAAAAAAA"
    b"AAAAAAgJ/9oADAMBAAIQAxAAAAEH0QSn/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQAB"
    b"BQJ//8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAgBAwEBPwF//8QAFBEBAAAAAAAAAAAAAAAA"
    b"AAAAAP/aAAgBAgEBPwF//8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQAGPwJ//8QAFBAB"
    b"AAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPyF//9oADAMBAAIAAwAAABAf/8QAFBEBAAAAAAAA"
    b"AAAAAAAAAAAAAP/aAAgBAwEBPxB//8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAgBAgEBPxB/"
    b"/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxB//9k="
)


class TestAnalysisFunctions(TestCase):

    def test_contrast(self):
        self.assertAlmostEqual(get_contrast(TEST_IMAGE), 46.84282228901243)

    def test_entropy(self):
        self.assertAlmostEqual(get_entropy(TEST_IMAGE), 3.584962500721156)

    def test_image_from_bytes(self):
        try:
            img = image_from_bytes(TEST_JPG)
        except UnidentifiedImageError:
            self.fail("Image conversion failed")
        self.assertIsInstance(img, Image)
        self.assertEqual(img.size, (1, 1))
