import hashlib

# Encrypt password using SHA-256
def encrypt_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()