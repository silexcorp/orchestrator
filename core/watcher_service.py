"""
watcher_service.py — Folder monitoring using the 'watchdog' library.
Mirrors WatchersView.swift and FSEvents integration.
"""
from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Optional, Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from models.schedule import Watcher


class _WatcherHandler(FileSystemEventHandler):
    def __init__(self, watcher: Watcher, on_change: Callable[[str, str], None]):
        self.watcher = watcher
        self.on_change = on_change
        self._last_trigger = 0

    def _handle(self, event):
        if event.is_directory:
            return
        
        # Debounce
        now = time.time()
        if (now - self._last_trigger) * 1000 < self.watcher.debounce_ms:
            return
        
        self._last_trigger = now
        self.on_change(self.watcher.id, event.src_path)

    def on_modified(self, event): self._handle(event)
    def on_created(self, event): self._handle(event)


class WatcherService:
    """
    Manages active folder watchers. When a file changes, it can trigger
    an AI agent to process the file.
    """

    def __init__(self):
        self._watchers: dict[str, Watcher] = {}
        self._observers: dict[str, Observer] = {}
        self._lock = threading.Lock()

    def start_watcher(self, watcher: Watcher, callback: Callable[[str, str], None]) -> bool:
        """Start monitoring a folder."""
        if not watcher.enabled or not Path(watcher.folder_path).exists():
            return False

        with self._lock:
            self.stop_watcher(watcher.id)
            
            observer = Observer()
            handler = _WatcherHandler(watcher, callback)
            observer.schedule(handler, watcher.folder_path, recursive=watcher.recursive)
            observer.start()
            
            self._watchers[watcher.id] = watcher
            self._observers[watcher.id] = observer
            return True

    def stop_watcher(self, watcher_id: str) -> None:
        """Stop monitoring a folder."""
        with self._lock:
            observer = self._observers.pop(watcher_id, None)
            if observer:
                observer.stop()
                observer.join()
            self._watchers.pop(watcher_id, None)

    def stop_all(self) -> None:
        with self._lock:
            for obs in self._observers.values():
                obs.stop()
            for obs in self._observers.values():
                obs.join()
            self._observers.clear()
            self._watchers.clear()


# Shared singleton
watcher_service = WatcherService()
