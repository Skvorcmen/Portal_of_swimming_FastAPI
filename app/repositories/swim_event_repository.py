from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models import SwimEvent
from app.repositories.base import BaseRepository


class SwimEventRepository(BaseRepository[SwimEvent]):
    def __init__(self, session: AsyncSession):
        super().__init__(SwimEvent, session)

    async def get_by_competition(self, competition_id: int) -> List[SwimEvent]:
        result = await self.session.execute(
            select(SwimEvent)
            .where(SwimEvent.competition_id == competition_id)
            .order_by(SwimEvent.order, SwimEvent.distance)
        )
        return result.scalars().all()
