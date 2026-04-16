# Profile Groups

Envoy lets you organize profiles into named groups, making it easy to apply batch operations or document which profiles belong to the same logical environment cluster.

## Commands

### Add a profile to a group

```bash
envoy group add <group> <profile>
```

Adds `<profile>` to `<group>`. The profile must already exist. Adding a profile that is already a member is a no-op.

### Remove a profile from a group

```bash
envoy group remove <group> <profile>
```

Removes `<profile>` from `<group>`. If the group becomes empty it is deleted automatically.

### List all groups

```bash
envoy group list
```

Prints all defined group names in alphabetical order.

### List members of a group

```bash
envoy group members <group>
```

Prints all profiles that belong to `<group>`.

### Delete a group

```bash
envoy group delete <group>
```

Deletes the group and all its memberships. Profiles themselves are not affected.

### Show groups for a profile

```bash
envoy group show <profile>
```

Prints all groups that `<profile>` belongs to.

## Storage

Group membership is stored in `~/.envoy/groups.json` (or the configured vault directory). The file is a plain JSON map of group name → list of profile names.

## Example

```bash
envoy set dev DB_URL postgres://localhost/dev
envoy set staging DB_URL postgres://staging/app

envoy group add backend dev
envoy group add backend staging

envoy group members backend
# dev
# staging

envoy group show dev
# backend
```
