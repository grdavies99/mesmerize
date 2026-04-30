import threading
import time
from typing import Callable

import mesmerize.playerctl as playerctl
from mesmerize.playerctl import PlayerctlError


class Observer:
    def __init__(self, callback: Callable[[dict], None], interval: float = 1.0):
        self._callback = callback
        self._interval = interval
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _loop(self) -> None:
        while not self._stop_event.wait(self._interval):
            try:
                self._callback({
                    "position": playerctl.get_position(),
                    "volume": playerctl.get_volume(),
                })
            except PlayerctlError:
                pass
