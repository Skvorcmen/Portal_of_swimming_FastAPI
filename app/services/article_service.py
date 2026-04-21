from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.repositories.article_repository import ArticleRepository
from app.models import Article


class ArticleService:
    def __init__(self, session: AsyncSession):
        self.repo = ArticleRepository(session)

    async def create_article(
        self,
        title: str,
        content: str,
        category: str,
        author_id: int,
        summary: Optional[str] = None,
    ) -> Article:
        return await self.repo.create(
            title=title,
            content=content,
            category=category,
            summary=summary,
            author_id=author_id,
        )

    async def publish_article(self, article_id: int) -> Optional[Article]:
        from datetime import datetime, timezone

        return await self.repo.update(
            article_id, is_published=True, published_at=datetime.now(timezone.utc)
        )

    async def get_article(self, article_id: int) -> Optional[Article]:
        return await self.repo.get_by_id(article_id)

    async def get_all_published(self, skip: int = 0, limit: int = 100) -> List[Article]:
        return await self.repo.get_published(skip, limit)

    async def get_by_category(self, category: str) -> List[Article]:
        return await self.repo.get_by_category(category)

    async def increment_views(self, article_id: int) -> None:
        await self.repo.increment_views(article_id)

    async def update_article(self, article_id: int, **kwargs) -> Optional[Article]:
        return await self.repo.update(article_id, **kwargs)

    async def delete_article(self, article_id: int) -> bool:
        return await self.repo.delete(article_id)

    async def search_articles(
        self, query: str = "", category: str = "", page: int = 1
    ) -> dict:
        return await self.repo.search(query, category, page)
