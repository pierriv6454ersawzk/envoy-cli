"""Notification hooks for envoy-cli events."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

VALID_CHANNELS = ("stdout", "file", "webhook")


def _notify_path(base_dir: str) -> Path:
    return Path(base_dir) / ".envoy" / "notify.json"


def _read_config(base_dir: str) -> dict:
    p = _notify_path(base_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _write_config(base_dir: str, config: dict) -> None:
    p = _notify_path(base_dir)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(config, indent=2))


def set_notify(base_dir: str, event: str, channel: str, target: Optional[str] = None) -> None:
    if channel not in VALID_CHANNELS:
        raise ValueError(f"Invalid channel '{channel}'. Choose from: {VALID_CHANNELS}")
    config = _read_config(base_dir)
    config.setdefault(event, [])  
    entry = {"channel": channel, "target": target}
    if entry not in config[event]:
        config[event].append(entry)
    _write_config(base_dir, config)


def remove_notify(base_dir: str, event: str, channel: str) -> bool:
    config = _read_config(base_dir)
    before = config.get(event, [])
    after = [e for e in before if e["channel"] != channel]
    if len(before) == len(after):
        return False
    config[event] = after
    _write_config(base_dir, config)
    return True


def list_notify(base_dir: str, event: Optional[str] = None) -> dict:
    config = _read_config(base_dir)
    if event:
        return {event: config.get(event, [])}
    return config


def dispatch(base_dir: str, event: str, message: str) -> list[str]:
    config = _read_config(base_dir)
    entries = config.get(event, [])
    dispatched = []
    for entry in entries:
        channel = entry["channel"]
        target = entry.get("target")
        if channel == "stdout":
            print(f"[envoy notify] {event}: {message}")
            dispatched.append("stdout")
        elif channel == "file" and target:
            Path(target).parent.mkdir(parents=True, exist_ok=True)
            with open(target, "a") as f:
                f.write(f"{event}: {message}\n")
            dispatched.append(f"file:{target}")
        elif channel == "webhook" and target:
            try:
                import urllib.request
                data = json.dumps({"event": event, "message": message}).encode()
                req = urllib.request.Request(target, data=data, headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=5)
                dispatched.append(f"webhook:{target}")
            except Exception:
                pass
    return dispatched
