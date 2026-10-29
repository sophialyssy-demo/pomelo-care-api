import hashlib
import time

import jwt

from . import config


def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash


def create_access_token(user_id: int, role: str) -> str:
    now = int(time.time())
    payload = {"sub": str(user_id), "role": role, "iat": now, "exp": now + config.JWT_TTL_SECONDS}
    token = jwt.encode(payload, config.JWT_SECRET, algorithm="HS256")
    return token.decode() if isinstance(token, bytes) else token


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, config.JWT_SECRET, options={"verify_exp": False})
