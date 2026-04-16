# Key Change History

envoy-cli tracks per-key change history within each profile vault, letting you audit how values have evolved over time.

## Overview

Every time a key is set or deleted, a history entry is recorded with:
- The **action** (`set`, `delete`)
- The **old** and **new** values
- A **timestamp**

History is stored in a sidecar file alongside the vault: `<profile>.history.json`.

## Commands

### Show history for a key

```bash
envoy history:show <profile> <key>
```

Displays a timestamped log of all recorded changes for the given key.

**Example:**
```
History for 'API_KEY' in profile 'production':
  [2024-06-01 10:22:01] SET: (none) -> 'abc123'
  [2024-06-03 14:05:44] SET: 'abc123' -> 'xyz789'
```

### List keys with history

```bash
envoy history:keys <profile>
```

Lists all keys in a profile that have at least one recorded history entry.

### Clear history for a key

```bash
envoy history:clear <profile> <key>
```

Removes all history entries for the specified key. Useful for pruning sensitive values from the log.

## Programmatic Usage

```python
from envoy.history import record_change, get_key_history, clear_key_history

record_change("production", "API_KEY", old_value=None, new_value="abc123", action="set")

entries = get_key_history("production", "API_KEY")
for e in entries:
    print(e["timestamp"], e["action"], e["old"], "->", e["new"])

clear_key_history("production", "API_KEY")
```

## Notes

- History is **not encrypted**. Avoid storing plaintext sensitive values if audit logs may be exposed.
- History files are profile-scoped and stored in the same vault directory.
- Deleting a profile vault file does **not** automatically remove its history file.
