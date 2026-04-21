from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.models import News
from app.repositories.base import BaseRepository
from sqlalchemy import select, desc, func


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

    from sqlalchemy import func, desc

    async def search(
        self, query: str = "", sort: str = "newest", page: int = 1, limit: int = 10
    ) -> dict:
        stmt = select(News).where(News.is_published == True)

        if query:
            stmt = stmt.where(
                (News.title.ilike(f"%{query}%")) | (News.content.ilike(f"%{query}%"))
            )

        if sort == "newest":
            stmt = stmt.order_by(desc(News.published_at))
        else:
            stmt = stmt.order_by(News.published_at)

        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        items = result.scalars().all()

        count_stmt = (
            select(func.count()).select_from(News).where(News.is_published == True)
        )
        if query:
            count_stmt = count_stmt.where(
                (News.title.ilike(f"%{query}%")) | (News.content.ilike(f"%{query}%"))
            )
        total = await self.session.scalar(count_stmt)

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total else 1,
        }
