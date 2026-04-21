from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional, List
from app.models import Heat, HeatEntry
from app.repositories.base import BaseRepository


class HeatRepository(BaseRepository[Heat]):
    def __init__(self, session: AsyncSession):
        super().__init__(Heat, session)

    async def get_by_swim_event(self, swim_event_id: int) -> List[Heat]:
        result = await self.session.execute(
            select(Heat)
            .where(Heat.swim_event_id == swim_event_id)
            .order_by(Heat.heat_number)
        )
        return result.scalars().all()


class HeatEntryRepository(BaseRepository[HeatEntry]):
    def __init__(self, session: AsyncSession):
        super().__init__(HeatEntry, session)

    async def get_by_heat(self, heat_id: int) -> List[HeatEntry]:
        result = await self.session.execute(
            select(HeatEntry)
            .where(HeatEntry.heat_id == heat_id)
            .order_by(HeatEntry.lane)
        )
        return result.scalars().all()

    async def update_result(self, heat_entry_id: int, result_time: float) -> HeatEntry:
        """Обновить результат участника"""
        return await self.update(heat_entry_id, result_time=result_time)
