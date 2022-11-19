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

from camfwd.act import KeyAct
from gphoto2 import Camera
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

stop = False


class CameraControl(Camera):

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

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, *_):
        self.exit()
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


def main(camera, command):
    key_actions = {}
    for key_config in INC_DEC_KEYS:
        key_actions.update(_inc_dec_action(camera, *key_config))
    with (
            Popen(command, bufsize=0, stdin=PIPE) as process,
            KeyAct(key_actions) as key_act):
        while not stop:
            _stream_image(camera, process.stdin)
            key_act.process_input()


if __name__ == "__main__":
    for sig in STOP_SIGNALS:
        signal(sig, _handle_signal)
    with CameraControl() as camera:
        main(camera, argv[1:])
