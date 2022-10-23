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
