"""Profile locking: prevent concurrent modifications to a vault profile."""

import os
import time
import json
from pathlib import Path
from envoy.profile import get_vault_dir

_LOCK_TIMEOUT = 30  # seconds before a stale lock is considered expired


def _lock_path(profile: str, base_dir: str | None = None) -> Path:
    return get_vault_dir(base_dir) / f"{profile}.lock"


def acquire_lock(profile: str, base_dir: str | None = None) -> bool:
    """Attempt to acquire a lock for *profile*.

    Returns True if the lock was acquired, False if already locked by another
    process (and the lock is not stale).
    """
    lock_file = _lock_path(profile, base_dir)

    if lock_file.exists():
        try:
            data = json.loads(lock_file.read_text())
            age = time.time() - data.get("ts", 0)
            if age < _LOCK_TIMEOUT:
                return False
        except (json.JSONDecodeError, OSError):
            pass  # treat corrupt / unreadable lock as stale

    lock_file.write_text(
        json.dumps({"pid": os.getpid(), "ts": time.time()})
    )
    return True


def release_lock(profile: str, base_dir: str | None = None) -> None:
    """Release the lock for *profile* if it is held by the current process."""
    lock_file = _lock_path(profile, base_dir)
    if not lock_file.exists():
        return
    try:
        data = json.loads(lock_file.read_text())
        if data.get("pid") == os.getpid():
            lock_file.unlink()
    except (json.JSONDecodeError, OSError):
        pass


def is_locked(profile: str, base_dir: str | None = None) -> bool:
    """Return True if *profile* is currently locked by another process."""
    lock_file = _lock_path(profile, base_dir)
    if not lock_file.exists():
        return False
    try:
        data = json.loads(lock_file.read_text())
        age = time.time() - data.get("ts", 0)
        return age < _LOCK_TIMEOUT and data.get("pid") != os.getpid()
    except (json.JSONDecodeError, OSError):
        return False


def lock_info(profile: str, base_dir: str | None = None) -> dict | None:
    """Return lock metadata dict or None if no active lock exists."""
    lock_file = _lock_path(profile, base_dir)
    if not lock_file.exists():
        return None
    try:
        data = json.loads(lock_file.read_text())
        age = time.time() - data.get("ts", 0)
        if age < _LOCK_TIMEOUT:
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return None
