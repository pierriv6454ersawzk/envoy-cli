# Template Rendering

`envoy` can render template files by substituting `{{ PLACEHOLDER }}` markers
with secrets stored in an encrypted vault profile.

## Template syntax

Use double-curly-brace placeholders anywhere in a plain-text file:

```
# config/database.yml
host: {{ DB_HOST }}
port: {{ DB_PORT }}
password: {{ DB_PASSWORD }}
```

Placeholder names must start with a letter or underscore and may contain
letters, digits, and underscores (`[A-Za-z_][A-Za-z0-9_]*`).  
Unknown placeholders are left untouched.

## Commands

### `template-render`

Render a template using secrets from a vault profile.

```bash
envoy template-render config/database.yml.tpl \
  --profile production \
  --passphrase "$ENVOY_PASS"
```

Write the result to a file instead of stdout:

```bash
envoy template-render config/database.yml.tpl \
  --profile production \
  --passphrase "$ENVOY_PASS" \
  --output config/database.yml
```

| Flag | Default | Description |
|---|---|---|
| `--profile` | `default` | Vault profile to read secrets from |
| `--passphrase` | *(required)* | Passphrase to decrypt the vault |
| `--output` | stdout | Write rendered output to this path |

### `template-inspect`

List every `{{ PLACEHOLDER }}` found in a template without decrypting anything:

```bash
envoy template-inspect config/database.yml.tpl
```

Example output:

```
Placeholders in database.yml.tpl:
  DB_HOST
  DB_PASSWORD
  DB_PORT
```

This is useful for auditing which secrets a template requires before
providing a passphrase.

## Python API

```python
from envoy.template import render_template, render_template_file, list_placeholders

# Render a string directly
rendered = render_template("HOST={{ HOST }}", {"HOST": "localhost"})

# Render a file backed by a vault
rendered = render_template_file(
    template_path="config.tpl",
    vault_path=".envoy/default.vault",
    passphrase="my-secret",
    output_path="config.rendered",  # optional
)

# Inspect placeholders without decrypting
keys = list_placeholders(open("config.tpl").read())
```
