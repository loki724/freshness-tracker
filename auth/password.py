import hashlib
import secrets

def generate_salt() -> str:
    return secrets.token_hex(16)

def hash_password(password: str, salt: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    key = hashlib.pbkdf2_hmac('sha256', pwd_bytes, salt_bytes, 100000)
    return key.hex()

def verify_password(plain_password: str, password_hash: str, salt: str) -> bool:
    new_hash = hash_password(plain_password, salt)
    return secrets.compare_digest(new_hash, password_hash)
