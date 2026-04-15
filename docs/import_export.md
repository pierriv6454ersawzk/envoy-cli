# Import & Export

Envoy supports importing and exporting `.env` files to and from encrypted vault profiles.

---

## Export

Export the variables from a profile to a plaintext `.env` file or print them to stdout.

```bash
# Print to stdout
envoy export --profile production --passphrase mysecret

# Write to a file
envoy export --profile production --passphrase mysecret --output .env.production

# Mask secret values (replaces values with ****)
envoy export --profile production --passphrase mysecret --mask
```

### Options

| Flag | Description |
|------|-------------|
| `--profile` | Profile to export (default: `default`) |
| `--passphrase` | Passphrase used to decrypt the vault |
| `--output` | File path to write to (omit for stdout) |
| `--mask` | Replace values with `****` in output |

---

## Import

Import key/value pairs from a `.env` file into an encrypted vault profile.

```bash
# Import into the default profile
envoy import --input .env.staging --passphrase mysecret

# Import into a named profile
envoy import --profile staging --input .env.staging --passphrase mysecret

# Overwrite existing keys
envoy import --profile staging --input .env.staging --passphrase mysecret --overwrite
```

### Options

| Flag | Description |
|------|-------------|
| `--profile` | Profile to import into (default: `default`) |
| `--passphrase` | Passphrase used to encrypt the vault |
| `--input` | Path to the `.env` file to import |
| `--overwrite` | Overwrite keys that already exist in the profile |

---

## Notes Exported files are **plaintext** — treat them with care and avoid committing them to version control.
- Import and export operations are recorded in the audit log.
- Comments and blank lines in imported `.env` files are ignored.
- If `--overwrite` is not set, existing keys are preserved during import.
