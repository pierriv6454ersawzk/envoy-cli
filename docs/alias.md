# Profile Aliases

Aliases let you assign short, memorable names to full profile names, reducing
typing and preventing mistakes when switching between environments.

## Commands

### Add an alias

```bash
envoy alias add <alias> <profile>
```

Maps `<alias>` to `<profile>`. If the alias already exists it is overwritten.

```bash
envoy alias add prod production
envoy alias add stg staging
envoy alias add dev development
```

### Remove an alias

```bash
envoy alias remove <alias>
```

Deletes the alias. Exits with an error if the alias does not exist.

```bash
envoy alias remove stg
```

### Resolve an alias

```bash
envoy alias show <alias>
```

Prints the profile name that `<alias>` points to.

```bash
$ envoy alias show prod
production
```

### List all aliases

```bash
envoy alias list
```

Displays every alias and the profile it resolves to:

```
  dev   ->  development
  prod  ->  production
```

## Storage

Aliases are stored in `~/.envoy/aliases.json` (or inside the directory set by
`ENVOY_BASE_DIR`). The file is a plain JSON object mapping alias strings to
profile name strings, making it easy to inspect or edit manually.

## Use with other commands

Alias resolution is intentionally kept as an explicit step — pipe the output
of `envoy alias show` into other commands when scripting:

```bash
envoy get $(envoy alias show prod) DB_URL --passphrase "$PASS"
```

This keeps the core commands simple while still benefiting from short names in
your daily workflow.
