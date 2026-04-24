# Pipelines

Pipelines let you define a named, ordered sequence of envoy operations tied to a specific profile. Once saved, a pipeline can be listed, inspected, and deleted.

## Concepts

| Term     | Meaning |
|----------|---------|
| Pipeline | A named list of steps associated with a profile |
| Step     | A single operation (e.g. `lint`, `snapshot`, `export`) |
| Action   | The operation type of a step |

### Supported Step Actions

| Action     | Description |
|------------|-------------|
| `copy`     | Copy keys from one profile to another |
| `merge`    | Merge another profile into this one |
| `lint`     | Run the linter against the profile |
| `validate` | Validate the profile against its schema |
| `snapshot` | Create a snapshot of the current state |
| `export`   | Export the profile to a `.env` file |

## Usage

### Save a pipeline

```bash
envoy pipeline-save deploy default '[{"action":"lint"},{"action":"snapshot"}]'
```

The third argument is a JSON array of step objects. Each object **must** include an `"action"` key.

### Show a pipeline

```bash
envoy pipeline-show deploy
```

Output:

```
Pipeline : deploy
Profile  : default
Steps    : 2
  1. lint
  2. snapshot
```

### List all pipelines

```bash
envoy pipeline-list
```

### Delete a pipeline

```bash
envoy pipeline-delete deploy
```

## Storage

Pipelines are stored in `~/.envoy/pipelines.json` (or the configured vault directory). The file is a plain JSON dictionary keyed by pipeline name.

## Notes

- A pipeline is tied to a single profile at definition time.
- The profile must exist when `pipeline-save` is called.
- Step parameters beyond `action` are stored as-is and may be used by future execution support.
- Saving a pipeline with an existing name **overwrites** the previous definition.
