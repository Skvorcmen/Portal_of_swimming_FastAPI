from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.models import News, NewsComment, NewsLike
from app.repositories.base import BaseRepository
from sqlalchemy import select, desc, func, or_
from sqlalchemy.orm import selectinload

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

    async def get_by_id_with_details(self, news_id: int) -> Optional[News]:
        result = await self.session.execute(
            select(News)
            .options(selectinload(News.author), selectinload(News.comments), selectinload(News.likes))
            .where(News.id == news_id)
        )
        return result.scalar_one_or_none()

    async def search(
        self, query: str = "", sort: str = "newest", page: int = 1, limit: int = 10
    ) -> dict:
        stmt = select(News).where(News.is_published == True).options(selectinload(News.author))

        if query:
            stmt = stmt.where(
                or_(
                    News.title.ilike(f"%{query}%"),
                    News.content.ilike(f"%{query}%"),
                    News.summary.ilike(f"%{query}%")
                )
            )

        if sort == "newest":
            stmt = stmt.order_by(desc(News.published_at))
        elif sort == "oldest":
            stmt = stmt.order_by(News.published_at)
        elif sort == "popular":
            stmt = stmt.order_by(desc(News.likes_count))

        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        items = result.scalars().all()

        count_stmt = select(func.count()).select_from(News).where(News.is_published == True)
        if query:
            count_stmt = count_stmt.where(
                or_(
                    News.title.ilike(f"%{query}%"),
                    News.content.ilike(f"%{query}%"),
                    News.summary.ilike(f"%{query}%")
                )
            )
        total = await self.session.scalar(count_stmt)

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total else 1,
        }

    async def toggle_like(self, news_id: int, user_id: int) -> dict:
        result = await self.session.execute(
            select(NewsLike).where(
                NewsLike.news_id == news_id,
                NewsLike.user_id == user_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            await self.session.delete(existing)
            news = await self.get_by_id(news_id)
            if news:
                news.likes_count = max(0, news.likes_count - 1)
                await self.session.commit()
            return {"liked": False, "likes_count": news.likes_count if news else 0}
        else:
            new_like = NewsLike(news_id=news_id, user_id=user_id)
            self.session.add(new_like)
            news = await self.get_by_id(news_id)
            if news:
                news.likes_count += 1
                await self.session.commit()
            return {"liked": True, "likes_count": news.likes_count if news else 0}

    async def add_comment(self, news_id: int, user_id: int, content: str) -> NewsComment:
        comment = NewsComment(news_id=news_id, user_id=user_id, content=content)
        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def get_comments(self, news_id: int, skip: int = 0, limit: int = 50) -> List[NewsComment]:
        result = await self.session.execute(
            select(NewsComment)
            .options(selectinload(NewsComment.user))
            .where(NewsComment.news_id == news_id)
            .order_by(desc(NewsComment.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def delete_comment(self, comment_id: int, user_id: int, is_admin: bool = False) -> bool:
        result = await self.session.execute(
            select(NewsComment).where(NewsComment.id == comment_id)
        )
        comment = result.scalar_one_or_none()
        if not comment:
            return False
        if comment.user_id != user_id and not is_admin:
            return False
        await self.session.delete(comment)
        await self.session.commit()
        return True
