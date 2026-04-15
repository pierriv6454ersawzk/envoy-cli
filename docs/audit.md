# Audit Log

envoy-cli maintains an **audit log** that records every significant action performed on your vault files. This helps you track who (or which process) accessed or modified your environment variables.

## What Gets Logged

The following actions are recorded automatically:

| Action | Trigger |
|--------|---------|
| `set` | A key is created or updated in a profile |
| `get` | A key is read from a profile |
| `delete` | A key is removed from a profile |
| `load` | A vault file is loaded/decrypted |
| `push` | A profile is pushed to a remote location |
| `pull` | A profile is pulled from a remote location |

Each entry contains:
- `timestamp` — ISO 8601 UTC timestamp
- `action` — the operation performed
- `profile` — which profile was affected
- `key` — the specific key (where applicable)

## Storage

The audit log is stored as a newline-delimited JSON file at:

```
~/.envoy/audit.log
```

You can override the vault directory via the `ENVOY_VAULT_DIR` environment variable.

## CLI Commands

### Show the audit log

```bash
envoy audit show
```

Filter by profile:

```bash
envoy audit show --profile production
```

Example output:

```
[2024-06-01T12:00:00+00:00] set         profile=default  key=API_KEY
[2024-06-01T12:01:00+00:00] get         profile=default  key=API_KEY
```

### Clear the audit log

```bash
envoy audit clear
```

You will be prompted to confirm. To skip the prompt:

```bash
envoy audit clear --force
```

## Privacy Note

The audit log stores **key names only** — never values. Vault contents remain encrypted at rest.
