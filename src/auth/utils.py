# Non-business logic functions: password hashing and JWT encoding/decoding
import hashlib
import hmac
import secrets
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import jwt

from src.auth.exceptions import InvalidToken

# OWASP recommended iteration count for PBKDF2-HMAC-SHA256
PASSWORD_HASH_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    """Return "<salt>$<hex digest>" of the password hashed with PBKDF2-HMAC-SHA256."""
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), PASSWORD_HASH_ITERATIONS).hex()
    return f"{salt}${digest}"


def verify_password(password: str, hashed_password: str) -> bool:
    """Check a plain password against a hash produced by hash_password."""
    try:
        salt, digest = hashed_password.split("$", 1)
    except ValueError:
        return False

    candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), PASSWORD_HASH_ITERATIONS).hex()
    return hmac.compare_digest(candidate, digest)


def create_access_token(subject: int, secret_key: str, algorithm: str, expires_minutes: int) -> str:
    """Encode a signed JWT whose "sub" claim is the given user id."""
    now = datetime.now(timezone.utc)
    payload = {"sub": str(subject), "iat": now, "exp": now + timedelta(minutes=expires_minutes)}
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_access_token(token: str, secret_key: str, algorithm: str) -> dict:
    """Decode and verify a JWT, raising InvalidToken on any failure."""
    try:
        return jwt.decode(token, secret_key, algorithms=[algorithm])
    except jwt.PyJWTError as error:
        raise InvalidToken() from error
