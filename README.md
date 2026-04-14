# envoy-cli

> A lightweight CLI for managing and syncing `.env` files across multiple project environments securely.

---

## Installation

```bash
pip install envoy-cli
```

Or install from source:

```bash
git clone https://github.com/yourname/envoy-cli.git && cd envoy-cli && pip install .
```

---

## Usage

```bash
# Initialize envoy in your project
envoy init

# Push your local .env to a named environment
envoy push --env production

# Pull the latest .env for an environment
envoy pull --env staging

# List all tracked environments
envoy list

# Sync .env across all environments
envoy sync --all
```

Envoy encrypts your secrets before storing or transmitting them, keeping credentials safe across teams and deployments.

---

## Configuration

Envoy looks for a `.envoy.toml` config file in your project root. Run `envoy init` to generate one automatically.

---

## Requirements

- Python 3.8+
- `cryptography`
- `click`

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any major changes.

---

## License

This project is licensed under the [MIT License](LICENSE).