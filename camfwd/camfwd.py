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

from camfwd.act import KeyAct, StandardIO
from camfwd.analysis import image_from_bytes, get_contrast, get_entropy
from gphoto2 import Camera, GPhoto2Error, GP_CAPTURE_IMAGE
from contextlib import contextmanager
from subprocess import Popen, PIPE
from sys import argv
from signal import signal, SIGTERM, SIGINT, SIGHUP

STOP_SIGNALS = SIGTERM, SIGINT, SIGHUP
INC_DEC_KEYS = (
    ("shutterspeed2", r"Shutter Speed: {}", "u", "j"),
    ("f-number", r"Focal Ratio: {}", "i", "k"),
    ("iso", r"Film Speed: {}", "o", "l")
)
FOCUS_STEPS = {
    "q": 1000, "a": -1000,
    "w": 100, "s": -100,
    "e": 10, "d": -10
}
ANALYSIS_MODES = (
    ("z", get_contrast, r"Contrast (Greyscale Standard Deviation): {:f}"),
    ("x", get_entropy, r"Entropy: {:f}")
)
CAPTURE_KEY = "\n"

stop = False


class CameraControl(Camera):

    def __init__(self, *args, vf_config="viewfinder", vf_value=1, **kwargs):
        self.vf_config = vf_config
        self.vf_value = vf_value
        super().__init__(*args, **kwargs)

    def get_frame(self):
        return bytes(self.capture_preview().get_data_and_size())

    def inc_dec_config(self, name, val):
        config = self.get_config()
        widget = config.get_child_by_name(name)
        current = widget.get_value()
        choices = tuple(widget.get_choices())
        index_new = choices.index(current) + val
        new = choices[index_new] if 0 <= index_new < len(choices) else current
        widget.set_value(new)
        self.set_config(config)
        return new

    def inc_config(self, config):
        return self.inc_dec_config(config, 1)

    def dec_config(self, config):
        return self.inc_dec_config(config, -1)

    def change_focus(
            self, amount, focus_widget="focusmode2", focus_value="4",
            focusdrive="manualfocusdrive"):
        config = self.get_config()
        config.get_child_by_name(focus_widget).set_value(focus_value)
        widget = config.get_child_by_name(focusdrive)
        widget.set_value(amount)
        try:
            self.set_config(config)
        except GPhoto2Error:
            pass

    def capture_image(self, capture_target="capturetarget", capture_value="1"):
        config = self.get_config()
        config.get_child_by_name(capture_target).set_value(capture_value)
        self.set_config(config)
        path = self.capture(GP_CAPTURE_IMAGE)
        return path.folder, path.name

    def open(self):
        self.init()
        vf = self.get_single_config(self.vf_config)
        vf.set_value(self.vf_value)
        self.set_single_config(self.vf_config, vf)
        return self

    def close(self):
        self.exit()

    def __enter__(self):
        return self.open()

    def __exit__(self, *_):
        self.close()
        return False


def _handle_signal(*_):
    global stop
    stop = True


def _stream_image(camera, stream):
    global stop
    image = camera.get_frame()
    try:
        stream.write(image)
    except OSError:
        stop = True


def _inc_dec_action(camera, config, fmt, inc, dec):
    def _function_generate(amp):
        def _inc_dec_internal():
            new = camera.inc_dec_config(config, amp)
            return fmt.format(new)
        return _inc_dec_internal
    return {inc: _function_generate(1), dec: _function_generate(-1)}


def _focus_action(camera, amount, key):
    def _focus_internal(_fmt="Focus: {}"):
        camera.change_focus(amount)
        return _fmt.format(f"{amount:+d}")
    return {key: _focus_internal}


def _pillow_analysis(camera, func, fmt):
    def _analysis_internal():
        pil_image = image_from_bytes(camera.get_frame())
        return fmt.format(func(pil_image))
    return _analysis_internal


def _capture(camera):
    def _capture_internal():
        path, name = camera.capture_image()
        return f"Image Captured: [Folder: {path}] [Name: {name}]"
    return _capture_internal


def main(camera, command):
    key_actions = {}
    for key_config in INC_DEC_KEYS:
        key_actions.update(_inc_dec_action(camera, *key_config))
    for key, step in FOCUS_STEPS.items():
        key_actions.update(_focus_action(camera, step, key))
    for key, *other in ANALYSIS_MODES:
        key_actions[key] = _pillow_analysis(camera, *other)
    key_actions[CAPTURE_KEY] = _capture(camera)
    with (
            Popen(command, bufsize=0, stdin=PIPE) as process,
            StandardIO() as stdio):
        key_act = KeyAct(key_actions, stdio)
        while not stop:
            _stream_image(camera, process.stdin)
            key_act.process_input()


if __name__ == "__main__":
    for sig in STOP_SIGNALS:
        signal(sig, _handle_signal)
    with CameraControl() as camera:
        main(camera, argv[1:])
