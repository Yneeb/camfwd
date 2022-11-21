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

from camfwd.camfwd import CameraControl
from gphoto2 import GPhoto2Error
from unittest import TestCase
from itertools import product
from time import sleep


def clamp(values, index, cur):
    return values[index if 0 <= index < len(values) else cur]


class TestCameraControl(TestCase):

    def setUp(self):
        self.cam_ctl = CameraControl()
        try:
            self.cam_ctl.open()
        except GPhoto2Error:
            self.skipTest("No camera connected")

    def tearDown(self):
        self.cam_ctl.close()

    def test_focus_control(self):
        SLEEP_TIMES = 0, 1
        TEST_AMPS = 1, 100, 1000, 10000, -1, -100, -1000, -10000
        for sleep_time, amp in product(SLEEP_TIMES, TEST_AMPS):
            with self.subTest(sleep_time=sleep_time, amp=amp):
                try:
                    self.cam_ctl.change_focus(amp)
                except GPhoto2Error:
                    self.fail()
                sleep(sleep_time)

    def test_inc_dec_config(self):
        SLEEP_TIMES = 0, .25
        TEST_CONFIGS = "iso", "shutterspeed2", "f-number"
        TEST_STEPS = 1, 10, 100, 1000, 10000, -1, -10, -100, -1000, -10000
        permutations = product(SLEEP_TIMES, TEST_CONFIGS, TEST_STEPS)
        for sleep_time, config, step in permutations:
            with self.subTest(sleep_time=sleep_time, config=config, step=step):
                widget = self.cam_ctl.get_config().get_child_by_name(config)
                choices = tuple(widget.get_choices())
                cur_ind = choices.index(widget.get_value())
                should_be = clamp(choices, cur_ind + step, cur_ind)
                ret = self.cam_ctl.inc_dec_config(config, step)
                self.assertEqual(ret, should_be)
                actual = self.cam_ctl.get_config().get_child_by_name(
                    config).get_value()
                self.assertEqual(actual, should_be)
                self.assertEqual(ret, actual)
                sleep(sleep_time)

    def test_frame_capture(self):
        JPEG_MAGIC = b"\xff\xd8\xff"
        image = self.cam_ctl.get_frame()
        self.assertIsInstance(image, bytes)
        self.assertTrue(image.startswith(JPEG_MAGIC))
