from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.constants.routes import AUTH_TOKEN_URL
from app.crud.user_crud import UserCRUD
from app.db.database import get_db
from app.models.user import User
from app.schemas.token import TokenPayload


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=AUTH_TOKEN_URL)

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        token_data = TokenPayload(**payload)
    except (JWTError, ValueError):
        raise credentials_exception
    
    user = await UserCRUD.get_user_by_id(db, user_id=token_data.sub)
    if not user:
        raise credentials_exception
    return user
