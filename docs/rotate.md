# Key Rotation

Key rotation lets you re-encrypt an existing vault profile under a new passphrase without losing any stored variables.

## Why rotate keys?

- A passphrase has been accidentally exposed.
- You want to enforce a regular passphrase-change policy.
- You are handing a project over to another team member.

## CLI usage

```bash
# Rotate the default profile
envoy rotate

# Rotate a named profile
envoy rotate staging
```

You will be prompted for:
1. **Current passphrase** – used to decrypt the vault.
2. **New passphrase** – the replacement passphrase.
3. **Confirm new passphrase** – must match the new passphrase exactly.

If the current passphrase is wrong, or the two new-passphrase entries do not match, the command exits with a non-zero status and the vault is left unchanged.

## Audit trail

Every successful rotation is recorded in the audit log with action `rotate_key`:

```bash
envoy audit show
# 2024-06-01T12:00:00 | rotate_key | profile=default
```

## Programmatic usage

```python
from envoy.rotate import rotate_key

rotate_key(
    profile="staging",
    old_passphrase="old-secret",
    new_passphrase="new-secret",
)
```

`rotate_key` raises `FileNotFoundError` when the profile does not exist and `ValueError` when the old passphrase is incorrect.

## Security notes

- Rotation is atomic at the file level: the vault file is only overwritten after the new ciphertext has been produced successfully.
- The old passphrase is never stored; make sure you remember the new one before rotating.
