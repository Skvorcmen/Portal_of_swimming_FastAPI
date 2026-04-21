from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from app.models import Article
from app.repositories.base import BaseRepository


class ArticleRepository(BaseRepository[Article]):
    def __init__(self, session: AsyncSession):
        super().__init__(Article, session)

    async def get_published(self, skip: int = 0, limit: int = 100) -> List[Article]:
        result = await self.session.execute(
            select(Article)
            .where(Article.is_published == True)
            .order_by(desc(Article.published_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_category(
        self, category: str, skip: int = 0, limit: int = 100
    ) -> List[Article]:
        result = await self.session.execute(
            select(Article)
            .where(Article.is_published == True, Article.category == category)
            .order_by(desc(Article.published_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def increment_views(self, article_id: int) -> None:
        article = await self.get_by_id(article_id)
        if article:
            await self.update(article_id, views=article.views + 1)
