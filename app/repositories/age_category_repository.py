from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models import AgeCategory
from app.repositories.base import BaseRepository


class AgeCategoryRepository(BaseRepository[AgeCategory]):
    """Репозиторий для работы с возрастными категориями"""

    def __init__(self, session: AsyncSession):
        super().__init__(AgeCategory, session)

    async def get_by_competition(self, competition_id: int) -> List[AgeCategory]:
        """Получить все возрастные категории для соревнования"""
        result = await self.session.execute(
            select(AgeCategory)
            .where(AgeCategory.competition_id == competition_id)
            .order_by(AgeCategory.min_age)
        )
        return result.scalars().all()

    async def get_by_competition_and_gender(
        self, competition_id: int, gender: str
    ) -> List[AgeCategory]:
        """Получить возрастные категории для соревнования по полу"""
        result = await self.session.execute(
            select(AgeCategory)
            .where(AgeCategory.competition_id == competition_id)
            .where(AgeCategory.gender == gender)
            .order_by(AgeCategory.min_age)
        )
        return result.scalars().all()
