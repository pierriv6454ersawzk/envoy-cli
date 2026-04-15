# Access Control

envoy-cli supports a lightweight access-control list (ACL) that lets you
associate human-readable **labels** (e.g. team names, user IDs, or roles) with
specific profiles.  This is useful for documenting and enforcing who is
allowed to work with a given environment vault.

## Concepts

| Term | Meaning |
|------|---------|
| **profile** | A named vault (e.g. `production`, `staging`) |
| **label** | An arbitrary string representing an identity or role |

The ACL is stored in `~/.envoy/vaults/access_control.json` (or inside the
configured `--base-dir`).

---

## Commands

### Grant access

```bash
envoy access-grant --profile production --label alice
```

Adds `alice` to the list of labels that may access the `production` profile.

### Revoke access

```bash
envoy access-revoke --profile production --label alice
```

Removes `alice` from the ACL for `production`.  If no labels remain the
profile entry is removed entirely.

### List labels for a profile

```bash
envoy access-list --profile production
```

Prints all labels that have been granted access to `production`.

### Show the full ACL

```bash
envoy access-show
```

Prints every profile together with its granted labels.

### Check a specific label

```bash
envoy access-check --profile production --label alice
```

Exits with code `0` if `alice` has access, or code `2` if not — suitable for
use in shell scripts and CI pipelines.

---

## Notes

- Labels are **not** tied to passphrases; they are metadata only.
- The ACL is stored in plain JSON — it is **not** encrypted.
- For passphrase rotation see `docs/rotate.md`.
