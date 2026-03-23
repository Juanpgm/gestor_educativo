"""Fernet-based encryption for PII fields stored in the database."""

from cryptography.fernet import Fernet, InvalidToken

from app.config import get_settings

settings = get_settings()

_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        _fernet = Fernet(settings.encryption_key.encode())
    return _fernet


def encrypt_value(plain_text: str) -> str:
    """Encrypt a plain-text string and return a URL-safe base64 token."""
    if not plain_text:
        return ""
    return _get_fernet().encrypt(plain_text.encode()).decode()


def decrypt_value(cipher_text: str) -> str:
    """Decrypt a Fernet token back to plain-text."""
    if not cipher_text:
        return ""
    try:
        return _get_fernet().decrypt(cipher_text.encode()).decode()
    except InvalidToken:
        return "***DECRYPTION_ERROR***"
