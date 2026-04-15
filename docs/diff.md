# Env Diff

The `diff` feature lets you compare two environment profiles — or a local profile against a remote snapshot — and see exactly what has changed.

## How it works

`envoy diff` loads the env key-value pairs from two sources, computes the symmetric difference, and renders a colour-coded summary:

| Prefix | Meaning |
|--------|---------|
| `+`    | Key exists only in the **right** (new) env |
| `-`    | Key exists only in the **left** (old) env |
| `~`    | Key exists in both but the **value changed** |

By default values are **masked** (`***`) to avoid leaking secrets in terminal output or CI logs. Pass `--show-values` to reveal them.

## CLI usage

```bash
# Compare two local profiles
envoy diff --profile staging --against production

# Compare local profile against its last pushed remote snapshot
envoy diff --profile staging --remote

# Show unchanged keys as well
envoy diff --profile staging --against production --show-unchanged

# Reveal actual values (use with care)
envoy diff --profile staging --against production --show-values
```

## Python API

```python
from envoy.diff import diff_envs, format_diff

left  = {"DB_HOST": "localhost", "SECRET": "old"}
right = {"DB_HOST": "localhost", "SECRET": "new", "NEW_KEY": "val"}

entries = diff_envs(left, right)
print(format_diff(entries, mask_values=False))
# Output:
#   + NEW_KEY = val
#   ~ SECRET: old -> new
```

## Security notes

- Values are masked by default in all output.
- The diff is computed entirely in-memory; nothing is written to disk.
- When diffing against a remote, the remote file is decrypted locally using your passphrase and never stored in plaintext.
