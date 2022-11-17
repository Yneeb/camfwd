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

from sys import stdin, stdout
from tty import setcbreak
from selectors import DefaultSelector, EVENT_READ

class KeyAct:

    def __init__(self, key_map, default=lambda: None, input=stdin, output=stdout):
        self.key_map = key_map
        self.default = default
        self.input = input
        self.output = output

    def __enter__(self):
        setcbreak(self.input.fileno())
        self.selector = DefaultSelector()
        self.selector.register(self.input, EVENT_READ)
        return self

    def __exit__(self, *_):
        self.selector.close()
        return False

    def _process_key(self, fileobj):
        key = fileobj.read(1)
        status = self.key_map.get(key, self.default)()
        if status is not None:
            self.output.write(f"{status}\n")

    def _process_events(self, events):
        processed = 0
        for key, mask in events:
            obj = key.fileobj
            if obj is not self.input:
                continue
            if not mask & EVENT_READ:
                continue
            self._process_key(obj)
        return processed

    def process_input(self):
        while self._process_events(self.selector.select(0)) > 0:
            pass
