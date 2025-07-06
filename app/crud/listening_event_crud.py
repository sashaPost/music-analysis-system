from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.listening_event import ListeningEvent
from app.schemas.listening_event import ListeningEventCreate


class ListeningEventCRUD:

    async def get_user_listening_history(
            self,
            db: AsyncSession,
            user_id: str,
            limit: int,
            offset: int
    ) -> Sequence[ListeningEvent]:
        result = await db.execute(
            select(ListeningEvent)
            .where(ListeningEvent.user_id == user_id)
            .order_by(ListeningEvent.played_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    @staticmethod
    async def get_event_by_id(
        db: AsyncSession, 
        event_id: int
    ) -> ListeningEvent | None:
        result = await db.execute(
            select(ListeningEvent).where(ListeningEvent.id == event_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_event(
        db: AsyncSession, 
        event_data: ListeningEventCreate
    ) -> ListeningEvent:
        event = ListeningEvent(**event_data.model_dump())
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event
