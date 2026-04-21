from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.news_service import NewsService
from app.models import User, UserRole
from app.core.dependencies import require_role

router = APIRouter(prefix="/news", tags=["news"])
templates = Jinja2Templates(directory="app/templates")


def get_news_service(db: AsyncSession = Depends(get_db)) -> NewsService:
    return NewsService(db)


class NewsCreate(BaseModel):
    title: str
    content: str


class NewsUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class NewsResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int | None
    is_published: bool
    published_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/test-page")
async def test_page(request: Request):
    return HTMLResponse("<h1>News page works!</h1>")


@router.get("/page")
async def news_page(request: Request):
    return templates.TemplateResponse("news_list.html", {"request": request})


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


@router.post("/", response_model=NewsResponse)
async def create_news(
    data: NewsCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: NewsService = Depends(get_news_service),
):
    return await service.create_news(
        title=data.title, content=data.content, author_id=current_user.id
    )


@router.post("/{news_id}/publish", response_model=NewsResponse)
async def publish_news(
    news_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: NewsService = Depends(get_news_service),
):
    news = await service.publish_news(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news


@router.get("/", response_model=List[NewsResponse])
async def get_all_news(
    skip: int = 0,
    limit: int = 100,
    service: NewsService = Depends(get_news_service),
):
    return await service.get_all_published(skip, limit)


@router.get("/{news_id}", response_model=NewsResponse)
async def get_news(
    news_id: int,
    service: NewsService = Depends(get_news_service),
):
    news = await service.get_news(news_id)
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    return news


@router.put("/{news_id}", response_model=NewsResponse)
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
