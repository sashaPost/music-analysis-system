from jose import jwt, JWTError
from fastapi import HTTPException, status
from app.config import settings


class AuthService:
    def decode_token(self, token: str) -> str:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: str = payload.get("sub")
            if not user_id:
                raise ValueError("Missing 'sub' in token")
            return user_id
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e
