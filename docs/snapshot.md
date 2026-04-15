# Snapshots

Snapshots let you capture the current state of a profile's environment variables at a point in time and restore them later. This is useful before deployments, migrations, or any risky configuration change.

## Creating a Snapshot

```bash
envoy snapshot create dev --passphrase mysecret
# Snapshot created: dev-1718000000000

# Attach a human-readable label
envoy snapshot create dev --passphrase mysecret --label before-v2-deploy
```

## Listing Snapshots

```bash
# All snapshots
envoy snapshot list

# Filter by profile
envoy snapshot list --profile dev
```

Example output:

```
dev-1718000000000  [before-v2-deploy]  profile=dev  2024-06-10 14:23:01
dev-1717900000000                      profile=dev  2024-06-09 10:05:44
```

## Restoring a Snapshot

Restoring overwrites the target profile's vault with the snapshot's data.

```bash
# Restore into the original profile
envoy snapshot restore dev-1718000000000 --passphrase mysecret

# Restore into a different profile
envoy snapshot restore dev-1718000000000 --passphrase mysecret --profile staging
```

> **Warning:** Restoring is destructive — the current state of the target profile will be replaced. Create a snapshot of it first if you need to preserve it.

## Deleting a Snapshot

```bash
envoy snapshot delete dev-1718000000000
```

## Storage Layout

Snapshots are stored inside the vault directory:

```
~/.envoy/
  snapshots/
    index.json          # metadata for all snapshots
    dev-<ts>.vault      # encrypted snapshot vault files
```

Each snapshot vault file is encrypted with the same passphrase used when the snapshot was created. You must supply the same passphrase to restore it.

## Security Notes

- Snapshot vault files use the same AES-GCM encryption as regular profile vaults.
- Labels and timestamps in `index.json` are stored in plaintext; avoid putting sensitive information in labels.
- Deleting a snapshot removes both the index entry and the encrypted vault file.
