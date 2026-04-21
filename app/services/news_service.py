from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.repositories.news_repository import NewsRepository
from app.models import News


class NewsService:
    def __init__(self, session: AsyncSession):
        self.repo = NewsRepository(session)

    async def create_news(self, title: str, content: str, author_id: int) -> News:
        return await self.repo.create(title=title, content=content, author_id=author_id)

    async def publish_news(self, news_id: int) -> Optional[News]:
        from datetime import datetime, timezone

        return await self.repo.update(
            news_id, is_published=True, published_at=datetime.now(timezone.utc)
        )

    async def get_news(self, news_id: int) -> Optional[News]:
        return await self.repo.get_by_id(news_id)

    async def get_all_published(self, skip: int = 0, limit: int = 100) -> List[News]:
        return await self.repo.get_published(skip, limit)

    async def update_news(self, news_id: int, **kwargs) -> Optional[News]:
        return await self.repo.update(news_id, **kwargs)

    async def delete_news(self, news_id: int) -> bool:
        return await self.repo.delete(news_id)

    async def search_news(
        self, query: str = "", sort: str = "newest", page: int = 1
    ) -> dict:
        return await self.repo.search(query, sort, page)
