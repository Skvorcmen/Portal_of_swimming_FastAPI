from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from app.models import News
from app.repositories.base import BaseRepository


class NewsRepository(BaseRepository[News]):
    def __init__(self, session: AsyncSession):
        super().__init__(News, session)

    async def get_published(self, skip: int = 0, limit: int = 100) -> List[News]:
        result = await self.session.execute(
            select(News)
            .where(News.is_published == True)
            .order_by(desc(News.published_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_author(self, author_id: int) -> List[News]:
        result = await self.session.execute(
            select(News)
            .where(News.author_id == author_id)
            .order_by(desc(News.created_at))
        )
        return result.scalars().all()
