import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode, urlsafe_b64decode


# Generate a hashed password
def hash_password(plain_password: str, salt: bytes = None) -> (str, str):
    if salt is None:
        # Generate a random 16-byte salt
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=SHA256(),
        length=32,  # Desired key length
        salt=salt,
        iterations=100_000,  # Number of iterations (recommended >= 100k)
        backend=default_backend(),
    )

    hashed_password = kdf.derive(plain_password.encode())
    return urlsafe_b64encode(hashed_password).decode(), urlsafe_b64encode(salt).decode()


# Verify a password
def verify_password(plain_password: str, hashed_password: str, salt: str) -> bool:
    kdf = PBKDF2HMAC(
        algorithm=SHA256(),
        length=32,
        salt=urlsafe_b64decode(salt),
        iterations=100_000,
        backend=default_backend(),
    )

    try:
        kdf.verify(plain_password.encode(), urlsafe_b64decode(hashed_password))
        return True
    except Exception:  # If verification fails
        return False
