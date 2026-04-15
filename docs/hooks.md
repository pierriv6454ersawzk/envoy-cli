# Hooks

envoy-cli supports lifecycle hooks — shell commands that run automatically when certain vault events occur.

## Supported Events

| Event | When it fires |
|---|---|
| `pre-set` | Before a key is written to a vault |
| `post-set` | After a key is written to a vault |
| `pre-load` | Before a vault is read/decrypted |
| `post-load` | After a vault is read/decrypted |
| `post-rotate` | After a vault passphrase is rotated |

## Commands

### Add a hook

```bash
envoy hook add post-set "echo 'Vault updated'"
envoy hook add post-rotate "./scripts/notify_team.sh"
```

### Remove a hook

```bash
envoy hook remove post-set "echo 'Vault updated'"
```

### List registered hooks

```bash
# All hooks
envoy hook list

# Filtered by event
envoy hook list --event post-set
```

Example output:

```
  [post-set] echo 'Vault updated'
  [post-rotate] ./scripts/notify_team.sh
```

### Manually trigger hooks

You can fire hooks for any event manually:

```bash
envoy hook run post-set
```

This is useful for testing or bootstrapping.

## Hook Storage

Hooks are stored in `.envoy/hooks.json` within your vault directory. They are not encrypted and are intended for local automation only.

## Environment Variables

Hooks inherit the current process environment, so any variables set before running envoy will be available inside hook scripts.

## Notes

- Hooks are local to the machine and **not synced** to remote storage.
- Multiple hooks can be registered for the same event; they run in registration order.
- If a hook command exits with a non-zero code, envoy logs the failure but continues.
