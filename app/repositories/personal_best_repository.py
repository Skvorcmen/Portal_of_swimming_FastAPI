from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.models import PersonalBest
from app.repositories.base import BaseRepository


class PersonalBestRepository(BaseRepository[PersonalBest]):
    def __init__(self, session: AsyncSession):
        super().__init__(PersonalBest, session)

    async def get_by_athlete(self, athlete_id: int) -> List[PersonalBest]:
        """Получить все рекорды спортсмена"""
        result = await self.session.execute(
            select(self.model)
            .where(self.model.athlete_id == athlete_id)
            .order_by(self.model.distance, self.model.time_seconds)
        )
        return result.scalars().all()


    async def get_by_id(self, pb_id: int):
        """Получить рекорд по ID"""
        from sqlalchemy import select
        result = await self.session.execute(
            select(self.model).where(self.model.id == pb_id)
        )
        return result.scalar_one_or_none()
