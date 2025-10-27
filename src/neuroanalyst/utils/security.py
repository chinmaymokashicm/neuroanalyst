import hashlib
import secrets
from cryptography.fernet import Fernet

def hash_password(password: str) -> str:
    """Hash a password using SHA256 (or upgrade to bcrypt later)."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hash_val: str) -> bool:
    """Verify password hash."""
    return hash_password(password) == hash_val

def generate_api_key() -> str:
    """Generate a random API key."""
    return secrets.token_urlsafe(32)

def generate_encryption_key() -> bytes:
    """Generate a Fernet-compatible key for encrypting/decrypting session data."""
    return Fernet.generate_key()

def encrypt_message(message: str, key: bytes) -> str:
    """Encrypt a message with Fernet symmetric key."""
    f = Fernet(key)
    return f.encrypt(message.encode()).decode()

def decrypt_message(token: str, key: bytes) -> str:
    """Decrypt a message with Fernet symmetric key."""
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()
