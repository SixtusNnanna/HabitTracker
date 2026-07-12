from ulid import ULID
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.config import settings


def create_access_token(payload: dict, expiry: timedelta | None = None):
    to_encode = payload.copy()
    expire = datetime.now(timezone.utc) + \
        (expiry or timedelta(minutes=settings.access_token_exp_time))
    to_encode.update({"exp": expire, "jti": str(ULID())})
    return jwt.encode(
        to_encode, key=settings.secrets, algorithm=settings.algorithm
    )


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token=token, key=settings.secrets,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        raise ValueError("Invalid or expires access token")




