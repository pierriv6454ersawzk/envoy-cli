# Sync

The `sync` feature allows you to **push** and **pull** encrypted `.env` vault profiles to and from a shared remote path (e.g. a mounted network share, S3-synced folder, or any file path accessible on your system).

## Commands

### Push a profile to a remote path

```bash
envoy push --profile prod --remote /mnt/shared/prod.env.enc
```

Encrypts your local `prod` profile and writes it to the specified remote path. The remote file is encrypted with the same passphrase.

---

### Pull a profile from a remote path

```bash
envoy pull --profile staging --remote /mnt/shared/staging.env.enc
```

Decrypts the remote vault file and saves it as the named local profile.

---

### Diff local vs remote

```bash
envoy diff --profile dev --remote /mnt/shared/dev.env.enc
```

Shows a table of keys that differ between the local and remote versions:

```
KEY                  LOCAL                REMOTE
--------------------------------------------------------------
API_URL              http://localhost      https://api.prod.io
DEBUG                true                 (missing)
```

---

### Remote configuration

You can store metadata about your remote backend using the `remote` subcommands:

```bash
# Store a config value
envoy remote set backend s3
envoy remote set bucket my-envoy-bucket

# View all stored config
envoy remote show
```

Remote config is stored in `.envoy_remote.json` inside your vault directory and is **not encrypted**. Do not store secrets here.

---

## Security Notes

- All data transferred via push/pull remains **AES-256 encrypted** using your passphrase.
- The passphrase is never written to disk or transmitted.
- The remote path can be any writable file path — envoy does not manage the transport layer itself.

## Typical Workflow

```bash
# Developer A sets a value and pushes
envoy set DATABASE_URL=postgres://... --profile prod
envoy push --profile prod --remote /shared/prod.env.enc

# Developer B pulls the latest
envoy pull --profile prod --remote /shared/prod.env.enc
envoy get DATABASE_URL --profile prod
```
