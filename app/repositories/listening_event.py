from abc import ABC, abstractmethod
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Sequence

from app.schemas.listening_event import ListeningEventCreate
from app.models.listening_event import ListeningEvent
from app.crud.listening_event_crud import ListeningEventCRUD


class ListeningEventRepository(ABC):
    @abstractmethod
    async def create_event(
        self,
        user_id: str,
        track_id: str,
        played_at: datetime,
        duration_ms: int
    ) -> ListeningEvent:
        pass

    @abstractmethod
    async def get_user_stats(self, user_id: str) -> dict[str, Any]:
        pass

    @abstractmethod
    async def get_user_listening_history(
        self, user_id: str, limit: int, offset: int
    ) -> Sequence[ListeningEvent]:
        pass


class SQLAlchemyListeningEventRepository(ListeningEventRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.crud = ListeningEventCRUD()

    async def create_event(
        self,
        user_id: str,
        track_id: str,
        played_at: datetime,
        duration_ms: int
    ) -> ListeningEvent:
        event_data = ListeningEventCreate(
            user_id=user_id,
            track_id=track_id,
            played_at=played_at,
            duration_ms=duration_ms,
            progress_ms=0,
            skipped=False
        )
        return await self.crud.create_event(self.session, event_data)
    
    async def get_user_stats(self, user_id: str) -> dict[str, Any]:
        result = await self.session.execute(
            select(
                func.count(ListeningEvent.id),
                func.sum(ListeningEvent.duration_ms),
                func.min(ListeningEvent.played_at),
                func.max(ListeningEvent.played_at)
            ).where(ListeningEvent.user_id == user_id)
        )

        total_count, total_duration, first_play, last_play = (
            result.one_or_none() or (0, 0, None, None)
        )

        return {
            "total_listens": total_count,
            "total_played_ms": total_duration or 0,
            "first_played": first_play,
            "last_played": last_play
        }
    
    async def get_user_listening_history(
        self, user_id: str, limit: int, offset: int
    ) -> Sequence[ListeningEvent]:
        from app.crud.listening_event_crud import ListeningEventCRUD
        return await ListeningEventCRUD().get_user_listening_history(
            self.session, user_id, limit, offset
        )
