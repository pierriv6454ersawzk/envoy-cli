"""Encryption and decryption utilities for .env file contents."""

import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet, InvalidToken


SALT_SIZE = 16
ITERATIONS = 390_000


def derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a passphrase and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))


def encrypt(plaintext: str, passphrase: str) -> bytes:
    """Encrypt plaintext using a passphrase.

    Returns salt + encrypted token as raw bytes.
    """
    salt = os.urandom(SALT_SIZE)
    key = derive_key(passphrase, salt)
    token = Fernet(key).encrypt(plaintext.encode())
    return salt + token


def decrypt(data: bytes, passphrase: str) -> str:
    """Decrypt data produced by :func:`encrypt`.

    Raises:
        ValueError: if the passphrase is wrong or data is corrupted.
    """
    salt, token = data[:SALT_SIZE], data[SALT_SIZE:]
    key = derive_key(passphrase, salt)
    try:
        return Fernet(key).decrypt(token).decode()
    except InvalidToken as exc:
        raise ValueError("Decryption failed: invalid passphrase or corrupted data.") from exc
