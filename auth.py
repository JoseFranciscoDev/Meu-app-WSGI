import hashlib
import hmac
import os


def generate_salt() -> str:
    return os.urandom(16).hex()


def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha512",
        password.encode(),
        bytes.fromhex(salt),
        260000,
    ).hex()


def verify_password(password: str, salt: str, stored_hash: str) -> bool:
    computed = hash_password(password, salt)
    return hmac.compare_digest(stored_hash, computed)
