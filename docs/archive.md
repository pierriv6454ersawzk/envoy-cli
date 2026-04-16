# Archive

The `archive` feature lets you bundle all current vault files into a compressed `.tar.gz` snapshot and restore them later.

## Overview

Archives differ from per-profile snapshots in that they capture **all profiles at once**, making them ideal for full backups before major changes.

## Commands

### Create an Archive

```bash
envoy archive create [--label LABEL]
```

Creates a compressed archive of all vault files. An optional `--label` can help identify the archive later.

**Example:**
```bash
envoy archive create --label before-migration
# Archive created: archive_1720000000.tar.gz
```

### List Archives

```bash
envoy archive list
```

Displays all available archives with their timestamps and labels.

```
archive_1720000000.tar.gz  2024-07-03 12:00:00  [before-migration]
archive_1720001000.tar.gz  2024-07-03 12:16:40
```

### Restore an Archive

```bash
envoy archive restore <name>
```

Extracts the archive and overwrites current vault files. Use with caution.

**Example:**
```bash
envoy archive restore archive_1720000000.tar.gz
# Restored from archive: archive_1720000000.tar.gz
```

### Delete an Archive

```bash
envoy archive delete <name>
```

Removes the archive file and its entry from the index.

## Storage

Archives are stored under `.envoy_archives/` in your base directory alongside an `index.json` metadata file.

## Notes

- Archives are not encrypted themselves — they contain already-encrypted vault files.
- For per-profile point-in-time snapshots, see [snapshot.md](snapshot.md).
