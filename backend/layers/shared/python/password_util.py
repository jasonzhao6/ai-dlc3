import hashlib
import secrets


def hash_password(password):
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f'{salt}:{h.hex()}'


def verify_password(password, stored_hash):
    try:
        salt, h = stored_hash.split(':')
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() == h
    except (ValueError, AttributeError):
        return False
