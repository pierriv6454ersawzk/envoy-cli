# Schema Validation

Envoy supports defining schemas for your profiles to enforce key presence and value types at validation time.

## Overview

A schema is a JSON file stored alongside your vault that describes what keys are expected, whether they are required, and what type their values should be.

Supported types:
- `string` (default)
- `integer`
- `float`
- `boolean` — accepts `true`, `false`, `1`, `0`, `yes`, `no` (case-insensitive)

---

## Commands

### `envoy schema set KEY [rules...]`

Define or update a schema rule for a key.

```bash
envoy schema set PORT required=true type=integer
envoy schema set DEBUG type=boolean
envoy schema set DATABASE_URL required=true description="Primary DB connection"
```

Available rule attributes:

| Attribute     | Values                              |
|---------------|-------------------------------------|
| `required`    | `true` / `false`                    |
| `type`        | `string`, `integer`, `float`, `boolean` |
| `description` | Free-text description               |

---

### `envoy schema show`

Display the full schema for a profile as JSON.

```bash
envoy schema show --profile production
```

---

### `envoy schema validate --passphrase <pass>`

Load the vault and check every key against the schema rules.

```bash
envoy schema validate --profile production --passphrase mysecret
```

Example output:

```
[ERROR] DATABASE_URL: required key is missing
[ERROR] PORT: expected integer, got 'eighty'
```

Exits with code `1` if any errors are found.

---

## Schema Storage

Schemas are stored in `.envoy/schemas/<profile>.json` inside your vault directory and are **not** encrypted. They describe structure, not secrets.

---

## Example Workflow

```bash
# Define schema for the production profile
envoy schema set PORT required=true type=integer --profile production
envoy schema set SECRET_KEY required=true --profile production
envoy schema set DEBUG type=boolean --profile production

# Validate before deploying
envoy schema validate --profile production --passphrase $ENVOY_PASS
```
