"""Unit tests for envoy.crypto."""

import pytest
from envoy.crypto import encrypt, decrypt


PASSPHRASE = "super-secret-passphrase"
PLAINTEXT = "DB_HOST=localhost\nDB_PASS=hunter2\n"


def test_encrypt_returns_bytes():
    result = encrypt(PLAINTEXT, PASSPHRASE)
    assert isinstance(result, bytes)


def test_encrypt_decrypt_roundtrip():
    ciphertext = encrypt(PLAINTEXT, PASSPHRASE)
    recovered = decrypt(ciphertext, PASSPHRASE)
    assert recovered == PLAINTEXT


def test_different_encryptions_produce_different_ciphertext():
    c1 = encrypt(PLAINTEXT, PASSPHRASE)
    c2 = encrypt(PLAINTEXT, PASSPHRASE)
    # Salt is random, so outputs must differ
    assert c1 != c2


def test_wrong_passphrase_raises_value_error():
    ciphertext = encrypt(PLAINTEXT, PASSPHRASE)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(ciphertext, "wrong-passphrase")


def test_corrupted_data_raises_value_error():
    ciphertext = bytearray(encrypt(PLAINTEXT, PASSPHRASE))
    ciphertext[20] ^= 0xFF  # flip a byte
    with pytest.raises(ValueError):
        decrypt(bytes(ciphertext), PASSPHRASE)
