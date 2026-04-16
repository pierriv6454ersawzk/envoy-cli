# Notifications

envoy-cli supports configurable notifications for vault events. You can route event alerts to stdout, a log file, or a webhook endpoint.

## Supported Events

| Event        | Triggered When                    |
|--------------|-----------------------------------|
| `on_set`     | A key is created or updated       |
| `on_delete`  | A key or profile is deleted       |
| `on_push`    | A profile is pushed to remote     |
| `on_pull`    | A profile is pulled from remote   |
| `on_rotate`  | A passphrase is rotated           |

## Channels

- **stdout** — Print notification to the terminal
- **file** — Append notification to a log file (`--target /path/to/log`)
- **webhook** — POST JSON payload to a URL (`--target https://...`)

## Commands

### Add a notification

```bash
envoy notify add on_set stdout
envoy notify add on_push file --target /var/log/envoy.log
envoy notify add on_rotate webhook --target https://hooks.example.com/envoy
```

### Remove a notification

```bash
envoy notify remove on_set stdout
```

### List notifications

```bash
envoy notify list
envoy notify list --event on_push
```

### Manually dispatch a notification

```bash
envoy notify dispatch on_set "API_KEY was updated"
```

## Webhook Payload

Webhook notifications send a JSON POST request:

```json
{
  "event": "on_set",
  "message": "API_KEY was updated"
}
```

## Storage

Notification configuration is stored in `.envoy/notify.json` within your vault directory.
