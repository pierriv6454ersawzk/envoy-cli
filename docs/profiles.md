# Envoy Profiles

Profiles let you manage multiple named environment configurations within the same project directory — for example, `dev`, `staging`, and `prod`.

## Storage

All profile vaults are stored under `.envoy/` in your project root:

```
.envoy/
  default.vault
  dev.vault
  staging.vault
  prod.vault
```

Each `.vault` file is independently encrypted with its own passphrase.

## Commands

### Set keys in a profile

```bash
envoy --profile dev set DB_HOST=localhost DB_PORT=5432
```

### Get a value from a profile

```bash
envoy --profile dev get DB_HOST
```

### List all keys in a profile

```bash
envoy --profile prod list
```

### List all available profiles

```bash
envoy profiles
```

### Delete a profile

```bash
envoy --profile staging delete-profile
```

## Profile Naming Rules

Profile names must contain only **letters, digits, hyphens (`-`), and underscores (`_`)**.

Invalid examples: `my profile`, `dev!`, `../etc`

## Security Notes

- Each profile is encrypted independently.
- Different profiles can (and should) use different passphrases.
- The `.envoy/` directory should be added to `.gitignore` unless you intentionally want to commit encrypted vaults.

## Recommended `.gitignore` entry

```
.envoy/
```
