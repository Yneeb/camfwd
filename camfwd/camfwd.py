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

from gphoto2 import Camera
from contextlib import contextmanager
from subprocess import Popen, PIPE
from sys import argv
from signal import signal, SIGTERM, SIGINT, SIGHUP

STOP_SIGNALS = SIGTERM, SIGINT, SIGHUP
stop = False

class CameraControl(Camera):

    def get_frame(self):
        return bytes(self.capture_preview().get_data_and_size())

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


def main(camera, command):
    with Popen(command, bufsize=0, stdin=PIPE) as process:
        while not stop:
            _stream_image(camera, process.stdin)


if __name__ == "__main__":
    for sig in STOP_SIGNALS:
        signal(sig, _handle_signal)
    with CameraControl() as camera:
        main(camera, argv[1:])
