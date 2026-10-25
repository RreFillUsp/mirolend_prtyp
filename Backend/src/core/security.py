# src/core/security.py
from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password with SHA256 first to handle long passwords."""
    # SHA256 hash first to ensure fixed length (64 bytes)
    sha256_hash = hashlib.sha256(password.encode()).hexdigest()
    # Then bcrypt
    return pwd_context.hash(sha256_hash)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    # Hash the plain password with SHA256 first
    sha256_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    return pwd_context.verify(sha256_hash, hashed_password)