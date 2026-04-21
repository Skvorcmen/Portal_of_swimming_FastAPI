from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.article_service import ArticleService
from app.models import User, UserRole
from app.core.dependencies import require_role

router = APIRouter(prefix="/articles", tags=["articles"])


def get_article_service(db: AsyncSession = Depends(get_db)) -> ArticleService:
    return ArticleService(db)


class ArticleCreate(BaseModel):
    title: str
    content: str
    category: str
    summary: str | None = None


class ArticleUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    category: str | None = None
    summary: str | None = None


class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    summary: str | None
    category: str
    author_id: int | None
    views: int
    is_published: bool
    published_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=ArticleResponse)
async def create_article(
    data: ArticleCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: ArticleService = Depends(get_article_service),
):
    return await service.create_article(
        title=data.title,
        content=data.content,
        category=data.category,
        summary=data.summary,
        author_id=current_user.id,
    )


@router.post("/{article_id}/publish", response_model=ArticleResponse)
async def publish_article(
    article_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: ArticleService = Depends(get_article_service),
):
    article = await service.publish_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.get("/", response_model=List[ArticleResponse])
async def get_all_articles(
    skip: int = 0,
    limit: int = 100,
    service: ArticleService = Depends(get_article_service),
):
    return await service.get_all_published(skip, limit)


@router.get("/category/{category}", response_model=List[ArticleResponse])
async def get_articles_by_category(
    category: str,
    service: ArticleService = Depends(get_article_service),
):
    return await service.get_by_category(category)


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    service: ArticleService = Depends(get_article_service),
):
    article = await service.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    # Увеличиваем счётчик просмотров
    await service.increment_views(article_id)
    return article


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    data: ArticleUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: ArticleService = Depends(get_article_service),
):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    article = await service.update_article(article_id, **update_data)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.delete("/{article_id}")
async def delete_article(
    article_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: ArticleService = Depends(get_article_service),
):
    deleted = await service.delete_article(article_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"message": "Article deleted successfully"}
