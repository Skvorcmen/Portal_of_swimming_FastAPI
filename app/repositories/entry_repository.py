from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional, List
from app.models import Entry
from app.repositories.base import BaseRepository


class EntryRepository(BaseRepository[Entry]):
    """Репозиторий для работы с заявками"""

    def __init__(self, session: AsyncSession):
        super().__init__(Entry, session)

    async def get_by_competition(self, competition_id: int) -> List[Entry]:
        """Получить все заявки для соревнования"""
        result = await self.session.execute(
            select(Entry)
            .where(Entry.competition_id == competition_id)
            .order_by(Entry.created_at)
        )
        return result.scalars().all()

    async def get_by_swim_event(self, swim_event_id: int) -> List[Entry]:
        """Получить все заявки для дистанции"""
        result = await self.session.execute(
            select(Entry)
            .where(Entry.swim_event_id == swim_event_id)
            .order_by(Entry.entry_time)
        )
        return result.scalars().all()

    async def get_by_athlete(self, athlete_id: int) -> List[Entry]:
        """Получить все заявки спортсмена"""
        result = await self.session.execute(
            select(Entry)
            .where(Entry.athlete_id == athlete_id)
            .order_by(Entry.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_status(self, status: str) -> List[Entry]:
        """Получить заявки по статусу"""
        result = await self.session.execute(select(Entry).where(Entry.status == status))
        return result.scalars().all()

    async def update_status(self, entry_id: int, status: str) -> Optional[Entry]:
        """Обновить статус заявки"""
        return await self.update(entry_id, status=status)
