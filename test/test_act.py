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

from camfwd.act import KeyAct, InternalIO
from unittest import TestCase
from functools import partial


class TestInternalIO(TestCase):

    def setUp(self):
        self.iio = InternalIO()

    def test_no_key(self):
        self.assertIsNone(self.iio.get_key())

    def test_single_key(self):
        TEST_KEY = "a"
        self.iio.output.append(TEST_KEY)
        self.assertEqual(self.iio.get_key(), TEST_KEY)
        self.assertIsNone(self.iio.get_key())

    def test_multiple_keys(self):
        TEST_KEYS = "camfwd"
        self.iio.output.extend(TEST_KEYS)
        for key in TEST_KEYS:
            self.assertEqual(self.iio.get_key(), key)
        self.assertIsNone(self.iio.get_key())

    def test_write(self):
        WRITE_STRING = "testing"
        self.iio.write(WRITE_STRING)
        self.assertEqual(self.iio.input.popleft(), WRITE_STRING)
        self.assertEqual(len(self.iio.input), 0)

    def test_multiple_writes(self):
        WRITES = "testing", "cam", "fwd"
        for write in WRITES:
            self.iio.write(write)
        for write in WRITES:
            self.assertEqual(self.iio.input.popleft(), write)
        self.assertEqual(len(self.iio.input), 0)


def generate_key_map(key_text):
    key_map = {}
    for key, text in key_text.items():
        key_map[key] = partial(str, text)
    return key_map


class TestKeyActProcessor(TestCase):

    KEY_ACT_MAP = {"c": "test1", "a": "test2"}

    def setUp(self):
        self.iio = InternalIO()
        self.ka = KeyAct(generate_key_map(self.KEY_ACT_MAP), self.iio)

    def test_key_press(self):
        key, text = next(iter(self.KEY_ACT_MAP.items()))
        self.iio.output.append(key)
        self.ka.process_input()
        ret = self.iio.input.popleft()
        self.assertEqual(f"{text}\n", ret)

    def test_multiple_key_presses(self):
        items = tuple(self.KEY_ACT_MAP.items())
        self.iio.output.extend(tuple(zip(*items))[0])
        for _ in range(len(items)):
            self.ka.process_input()
        for text in tuple(zip(*items))[1]:
            ret = self.iio.input.popleft()
            self.assertEqual(f"{text}\n", ret)


class TestKeyActDefault(TestCase):

    def setUp(self):
        self.iio = InternalIO()

    def test_default_default(self):
        TEST_KEY = "c"
        ka = KeyAct({}, self.iio)
        self.iio.output.append(TEST_KEY)
        ka.process_input()
        self.assertEqual(len(self.iio.input), 0)

    def test_custom_default(self):
        TEST_KEY = "c"
        CUSTOM_STRING = "camfwd"

        def custom_default():
            return CUSTOM_STRING
        ka = KeyAct({}, self.iio, default=custom_default)
        self.iio.output.append(TEST_KEY)
        ka.process_input()
        self.assertEqual(self.iio.input.popleft(), f"{CUSTOM_STRING}\n")
