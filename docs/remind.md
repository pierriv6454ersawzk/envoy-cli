# Reminders

The `remind` feature lets you attach time-based reminder messages to keys within a profile. This is useful for flagging keys that need rotation, review, or follow-up by a specific date.

## Concepts

- A **reminder** is associated with a `(profile, key)` pair.
- Each reminder has a **message** and a **due** time (Unix timestamp).
- Reminders whose due time has passed are considered **overdue**.

## Commands

### Set a reminder

```bash
envoy remind-set <profile> <key> "<message>" --due <unix-timestamp>
```

Example:

```bash
envoy remind-set production DB_PASSWORD "Rotate this key" --due 1735689600
```

### Remove a reminder

```bash
envoy remind-remove <profile> <key>
```

### Show a reminder

```bash
envoy remind-show <profile> <key>
```

Output:
```
Key:     DB_PASSWORD
Message: Rotate this key
Due:     2025-01-01 00:00:00
```

### List all reminders for a profile

```bash
envoy remind-list <profile>
```

### List overdue reminders

```bash
envoy remind-due <profile>
```

Only reminders whose due timestamp is in the past will be shown.

## Storage

Reminders are stored in `reminders.json` inside the vault directory. They are not encrypted — only the message text and due timestamp are stored.

## Notes

- You cannot set a reminder with a due time in the past.
- Setting a reminder on a non-existent profile raises an error.
- Reminders are per-key: each key can have at most one active reminder.
