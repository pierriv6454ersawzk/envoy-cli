"""watch.py – Monitor a .env vault file for changes and trigger a callback."""

from __future__ import annotations

import os
import time
import threading
from typing import Callable, Optional


class VaultWatcher:
    """Poll a vault file for mtime changes and invoke a callback on change."""

    def __init__(
        self,
        path: str,
        callback: Callable[[str], None],
        interval: float = 1.0,
    ) -> None:
        self.path = path
        self.callback = callback
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_mtime: Optional[float] = self._current_mtime()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start watching in a background daemon thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Signal the watcher to stop and wait for the thread to exit."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=self.interval * 2)
            self._thread = None

    def is_alive(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _current_mtime(self) -> Optional[float]:
        try:
            return os.path.getmtime(self.path)
        except FileNotFoundError:
            return None

    def _run(self) -> None:
        while not self._stop_event.is_set():
            mtime = self._current_mtime()
            if mtime != self._last_mtime:
                self._last_mtime = mtime
                try:
                    self.callback(self.path)
                except Exception:  # noqa: BLE001 – watcher must not crash
                    pass
            self._stop_event.wait(self.interval)


def watch_profile(
    path: str,
    callback: Callable[[str], None],
    interval: float = 1.0,
) -> VaultWatcher:
    """Convenience factory: create, start, and return a VaultWatcher."""
    watcher = VaultWatcher(path, callback, interval)
    watcher.start()
    return watcher
