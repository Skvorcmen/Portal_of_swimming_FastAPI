from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.news_service import NewsService
from app.models import User, UserRole
from app.core.dependencies import require_role
from app.auth import get_current_user_optional_cookie, get_current_active_user
from app.core.csrf import verify_csrf_token

router = APIRouter(prefix="/news", tags=["news"])
templates = Jinja2Templates(directory="app/templates")


def get_news_service(db: AsyncSession = Depends(get_db)) -> NewsService:
    return NewsService(db)


# Схемы
class NewsCreate(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None


class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None


class CommentCreate(BaseModel):
    content: str


# Страницы
@router.get("/page")
async def news_page(
    request: Request,
    current_user: User = Depends(get_current_user_optional_cookie),
):
    return templates.TemplateResponse(
        "news_list.html", {"request": request, "current_user": current_user}
    )


@router.get("/search")
async def search_news(
    request: Request,
    q: str = "",
    sort: str = "newest",
    page: int = 1,
    service: NewsService = Depends(get_news_service),
):
    result = await service.search_news(q, sort, page)
    return templates.TemplateResponse(
        "partials/news_items.html",
        {
            "request": request,
            "news_list": result["items"],
            "q": q,
            "page": page,
            "sort": sort,
            "total": result["total"],
            "pages": result["pages"],
        },
    )


@router.get("/{news_id}")
async def get_news(
    news_id: int,
    request: Request,
    current_user: User = Depends(get_current_user_optional_cookie),
    service: NewsService = Depends(get_news_service),
):
    news = await service.get_news(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    user_liked = False
    if current_user:
        user_liked = await service.get_user_liked(news_id, current_user.id)

    comments = await service.get_comments(news_id)

    return templates.TemplateResponse(
        "news_detail.html",
        {
            "request": request,
            "news": news,
            "current_user": current_user,
            "user_liked": user_liked,
            "comments": comments,
        },
    )


# API эндпоинты


@router.post("/")
async def create_news(
    data: NewsCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: NewsService = Depends(get_news_service),
):
    return await service.create_news(
        title=data.title,
        content=data.content,
        summary=data.summary,
        image_url=data.image_url,
        video_url=data.video_url,
        author_id=current_user.id,
    )


@router.post("/{news_id}/publish")
async def publish_news(
    news_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: NewsService = Depends(get_news_service),
):
    news = await service.publish_news(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news


@router.post("/{news_id}/like")
async def toggle_like(
    news_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    service: NewsService = Depends(get_news_service),
):
    verify_csrf_token(request)
    result = await service.toggle_like(news_id, current_user.id)
    return JSONResponse(content=result)


@router.post("/{news_id}/comments")
async def add_comment(
    news_id: int,
    data: CommentCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    service: NewsService = Depends(get_news_service),
):
    verify_csrf_token(request)
    comment = await service.add_comment(news_id, current_user.id, data.content)
    return {
        "id": comment.id,
        "content": comment.content,
        "created_at": comment.created_at.isoformat(),
        "user_name": current_user.full_name,
        "user_id": current_user.id,
    }


@router.get("/{news_id}/comments")
async def get_comments(
    news_id: int,
    skip: int = 0,
    limit: int = 50,
    service: NewsService = Depends(get_news_service),
):
    comments = await service.get_comments(news_id, skip, limit)
    return [
        {
            "id": c.id,
            "content": c.content,
            "created_at": c.created_at.isoformat(),
            "user_id": c.user_id,
            "user_name": c.user.full_name if c.user else "Unknown",
        }
        for c in comments
    ]


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    service: NewsService = Depends(get_news_service),
):
    verify_csrf_token(request)
    is_admin = current_user.role == UserRole.ADMIN
    deleted = await service.delete_comment(comment_id, current_user.id, is_admin)
    if not deleted:
        raise HTTPException(
            status_code=404, detail="Comment not found or not authorized"
        )
    return {"message": "Comment deleted"}


@router.put("/{news_id}")
async def update_news(
    news_id: int,
    data: NewsUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: NewsService = Depends(get_news_service),
):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    news = await service.update_news(news_id, **update_data)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news


@router.delete("/{news_id}")
async def delete_news(
    news_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: NewsService = Depends(get_news_service),
):
    deleted = await service.delete_news(news_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="News not found")
    return {"message": "News deleted successfully"}
