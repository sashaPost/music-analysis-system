from fastapi import HTTPException
from jose import JWTError
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch, MagicMock

from app.api.deps import get_current_user
from app.models.user import User


@pytest.mark.asyncio
@patch("app.api.deps.jwt.decode")
async def test_get_current_user_success(mock_decode) -> None:
    user_id = "user-123"
    mock_decode.return_value = {"sub": user_id}

    mock_user = User(id=user_id, username="test", email="test@example.com")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user

    db: AsyncSession = AsyncMock()
    db.execute.return_value = mock_result

    user = await get_current_user(token="dummy.token", db=db)
    assert user == mock_user


@patch("app.api.deps.jwt.decode")
async def test_get_current_user_invalid_token(mock_decode) -> None:
    mock_decode.side_effect = JWTError("bad token")
    db: AsyncSession = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await get_current_user(token="bad.token", db=db)

    assert exc.value.status_code == 401
    assert "Could not validate credentials" in str(exc.value.detail)


@pytest.mark.asyncio
@patch("app.api.deps.jwt.decode")
async def test_get_current_user_missing_sub(mock_decode) -> None:
    mock_decode.return_value = {}  
    db: AsyncSession = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await get_current_user(token="missing-sub.token", db=db)

    assert exc.value.status_code == 401


@pytest.mark.asyncio
@patch("app.api.deps.jwt.decode")
async def test_get_current_user_user_not_found(mock_decode) -> None:
    mock_decode.return_value = {"sub": "not-in-db"}

    db: AsyncSession = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await get_current_user(token="valid.token", db=db)

    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"
