from datetime import datetime, timedelta, timezone
from typing import Any
import jwt

from app.config import settings

SECRET_KEY = settings.secret_key
ALGORYTHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(
        data: dict[str, Any],
        expires_delta: timedelta | None = None
) -> str:
    """
    Create a JWT access token with an expiration time.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORYTHM
    )
    return encoded_jwt
