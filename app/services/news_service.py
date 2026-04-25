from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.repositories.news_repository import NewsRepository
from app.models import News, NewsComment


class NewsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = NewsRepository(session)

    async def create_news(
        self,
        title: str,
        content: str,
        author_id: int,
        summary: Optional[str] = None,
        image_url: Optional[str] = None,
        video_url: Optional[str] = None,
    ) -> News:
        return await self.repo.create(
            title=title,
            content=content,
            summary=summary,
            image_url=image_url,
            video_url=video_url,
            author_id=author_id,
        )

    async def publish_news(self, news_id: int) -> Optional[News]:
        from datetime import datetime, timezone
        return await self.repo.update(
            news_id, is_published=True, published_at=datetime.now(timezone.utc)
        )

    async def get_news(self, news_id: int) -> Optional[News]:
        return await self.repo.get_by_id(news_id)

    async def get_news_with_details(self, news_id: int) -> Optional[News]:
        return await self.repo.get_by_id_with_details(news_id)

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

    async def toggle_like(self, news_id: int, user_id: int) -> dict:
        return await self.repo.toggle_like(news_id, user_id)

    async def add_comment(self, news_id: int, user_id: int, content: str) -> NewsComment:
        return await self.repo.add_comment(news_id, user_id, content)

    async def get_comments(self, news_id: int, skip: int = 0, limit: int = 50) -> List[NewsComment]:
        return await self.repo.get_comments(news_id, skip, limit)

    async def delete_comment(self, comment_id: int, user_id: int, is_admin: bool = False) -> bool:
        return await self.repo.delete_comment(comment_id, user_id, is_admin)

    async def get_user_liked(self, news_id: int, user_id: int) -> bool:
        from sqlalchemy import select
        from app.models import NewsLike
        result = await self.session.execute(
            select(NewsLike).where(
                NewsLike.news_id == news_id,
                NewsLike.user_id == user_id
            )
        )
        return result.scalar_one_or_none() is not None
