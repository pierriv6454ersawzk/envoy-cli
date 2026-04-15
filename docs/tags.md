# Profile Tags

envoy-cli lets you attach arbitrary **tags** to profiles, making it easy to group,
filter, and discover profiles by role, environment tier, or any custom label.

---

## Commands

### Add a tag

```bash
envoy tag add <profile> <tag>
```

Example:

```bash
envoy tag add production live
envoy tag add production critical
```

### Remove a tag

```bash
envoy tag remove <profile> <tag>
```

### List tags for a profile

```bash
envoy tag list <profile>
```

Example output:

```
live
critical
```

### Find profiles by tag

```bash
envoy tag find <tag>
```

Returns all profiles that carry the specified tag:

```
production
staging
```

### Show all tags

```bash
envoy tag all
```

Displays the full profile-to-tags mapping:

```
dev: local
production: live, critical
staging: live
```

---

## Storage

Tags are stored in a single JSON index file inside the vault directory:

```
~/.envoy/tags.json
```

The file is human-readable and can be committed to version control if desired
(it contains no secrets).

---

## Use cases

| Tag | Purpose |
|-----|---------|
| `live` | Marks profiles connected to live infrastructure |
| `readonly` | Profiles that should never be mutated via CLI |
| `ci` | Profiles used in continuous integration pipelines |
| `deprecated` | Profiles scheduled for removal |

Combine with `envoy search` to build powerful filtering workflows:

```bash
# Find all "live" profiles, then inspect each one
for profile in $(envoy tag find live); do
  envoy list --profile "$profile"
done
```
