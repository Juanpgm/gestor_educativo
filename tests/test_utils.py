"""Tests for utility / core functions (security, encryption)."""

import time

import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.utils.encryption import decrypt_value, encrypt_value


# ═══════════════════════════════════════════════════════════════
# Security
# ═══════════════════════════════════════════════════════════════


class TestPasswordHashing:
    def test_hashes_are_different_from_plain(self):
        hashed = hash_password("SecurePass123!")
        assert hashed != "SecurePass123!"

    def test_verify_correct_password(self):
        hashed = hash_password("SecurePass123!")
        assert verify_password("SecurePass123!", hashed)

    def test_verify_wrong_password(self):
        hashed = hash_password("SecurePass123!")
        assert not verify_password("WrongPassword!", hashed)

    def test_same_password_different_hashes(self):
        """bcrypt uses random salt, so hashes differ."""
        h1 = hash_password("SamePass!")
        h2 = hash_password("SamePass!")
        assert h1 != h2
        assert verify_password("SamePass!", h1)
        assert verify_password("SamePass!", h2)

    def test_empty_password(self):
        hashed = hash_password("")
        assert verify_password("", hashed)
        assert not verify_password("notempty", hashed)


class TestJWT:
    def test_access_token_payload(self):
        token = create_access_token({"sub": "42", "rol": "admin"})
        payload = decode_token(token)
        assert payload["sub"] == "42"
        assert payload["rol"] == "admin"
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_refresh_token_payload(self):
        token = create_refresh_token({"sub": "7", "rol": "secretaria"})
        payload = decode_token(token)
        assert payload["sub"] == "7"
        assert payload["rol"] == "secretaria"
        assert payload["type"] == "refresh"

    def test_decode_invalid_token(self):
        assert decode_token("not.a.jwt") is None

    def test_decode_tampered_token(self):
        token = create_access_token({"sub": "1"})
        # Tamper with the last character
        tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
        assert decode_token(tampered) is None

    def test_decode_empty_string(self):
        assert decode_token("") is None

    def test_token_different_data(self):
        t1 = create_access_token({"sub": "1"})
        t2 = create_access_token({"sub": "2"})
        assert t1 != t2
        assert decode_token(t1)["sub"] == "1"
        assert decode_token(t2)["sub"] == "2"


# ═══════════════════════════════════════════════════════════════
# Encryption
# ═══════════════════════════════════════════════════════════════


class TestEncryption:
    def test_encrypt_decrypt_roundtrip(self):
        original = "1234567890"
        encrypted = encrypt_value(original)
        assert encrypted != original
        assert decrypt_value(encrypted) == original

    def test_empty_string(self):
        """Empty strings are returned as-is (falsy)."""
        assert encrypt_value("") == ""
        assert decrypt_value("") == ""

    def test_encrypt_produces_different_ciphertexts(self):
        """Fernet includes a timestamp, so same input gives different output."""
        e1 = encrypt_value("hello")
        e2 = encrypt_value("hello")
        # Both should decrypt to the same value
        assert decrypt_value(e1) == "hello"
        assert decrypt_value(e2) == "hello"

    def test_unicode_roundtrip(self):
        original = "José María Ñoño 日本語"
        encrypted = encrypt_value(original)
        assert decrypt_value(encrypted) == original

    def test_long_value(self):
        original = "A" * 10_000
        assert decrypt_value(encrypt_value(original)) == original

    def test_decrypt_invalid_token(self):
        result = decrypt_value("not-a-valid-fernet-token")
        assert result == "***DECRYPTION_ERROR***"

    def test_decrypt_corrupted_data(self):
        encrypted = encrypt_value("secret")
        corrupted = encrypted[:10] + "XXXX" + encrypted[14:]
        result = decrypt_value(corrupted)
        assert result == "***DECRYPTION_ERROR***"
