"""Vault: read/write encrypted .env files on disk."""

from pathlib import Path
from typing import Dict

from envoy.crypto import encrypt, decrypt

DEFAULT_VAULT_SUFFIX = ".vault"


def _parse_env(text: str) -> Dict[str, str]:
    """Parse KEY=VALUE lines, ignoring comments and blank lines."""
    env: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def _serialize_env(env: Dict[str, str]) -> str:
    """Serialize a dict back to KEY=VALUE format."""
    return "\n".join(f"{k}={v}" for k, v in env.items()) + "\n"


def save(env: Dict[str, str], path: Path, passphrase: str) -> None:
    """Encrypt *env* and write it to *path*."""
    plaintext = _serialize_env(env)
    ciphertext = encrypt(plaintext, passphrase)
    path.write_bytes(ciphertext)


def load(path: Path, passphrase: str) -> Dict[str, str]:
    """Read and decrypt an env vault file from *path*.

    Raises:
        FileNotFoundError: if *path* does not exist.
        ValueError: if decryption fails.
    """
    if not path.exists():
        raise FileNotFoundError(f"Vault file not found: {path}")
    ciphertext = path.read_bytes()
    plaintext = decrypt(ciphertext, passphrase)
    return _parse_env(plaintext)
