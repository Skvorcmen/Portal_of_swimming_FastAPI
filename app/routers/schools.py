from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.school_service import SchoolService
from app.models import User, UserRole, CoachProfile, Branch
from app.core.dependencies import require_role

router = APIRouter(prefix="/schools", tags=["schools"])
templates = Jinja2Templates(directory="app/templates")

def get_school_service(db: AsyncSession = Depends(get_db)) -> SchoolService:
    return SchoolService(db)

@router.get("/{school_id}/page")
async def school_detail_page(
    school_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    school_service = SchoolService(db)
    
    school = await school_service.get_school(school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    
    # Получаем филиалы школы
    branches = await school_service.get_branches(school_id)
    
    # Получаем главного тренера школы (is_head_coach = True)
    head_coach_result = await db.execute(
        select(CoachProfile)
        .options(selectinload(CoachProfile.user))
        .where(CoachProfile.school_id == school_id, CoachProfile.is_head_coach == True)
    )
    head_coach = head_coach_result.scalar_one_or_none()
    
    return templates.TemplateResponse(
        "school_detail.html", 
        {
            "request": request, 
            "school": school, 
            "branches": branches,
            "head_coach": head_coach,
            "now": datetime.now()
        }
    )

# ... остальные эндпоинты (GET, POST, PUT, DELETE) остаются без изменений ...

@router.get("/page")
async def schools_list_page(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Страница со списком школ"""
    service = get_school_service(db)
    schools = await service.get_all_schools()
    return templates.TemplateResponse(
        "schools_list.html",
        {"request": request, "schools": schools}
    )

@router.get("/search")
async def search_schools(
    request: Request,
    name: str = "",
    city: str = "",
    page: int = 1,
    db: AsyncSession = Depends(get_db)
):
    """Поиск школ (для HTMX)"""
    service = SchoolService(db)
    result = await service.search_schools(name, city, page)
    
    return templates.TemplateResponse(
        "partials/school_items.html",
        {
            "request": request,
            "schools": result["items"],
            "page": page,
            "total": result["total"],
            "pages": result["pages"],
        }
    )
