from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List
from pydantic import BaseModel
from datetime import datetime, timezone

from app.database import get_db
from app.services.coach_service import CoachService
from app.services.school_service import SchoolService
from app.models import User, UserRole
from app.core.dependencies import require_role

router = APIRouter(prefix="/coaches", tags=["coaches"])
templates = Jinja2Templates(directory="app/templates")

def get_coach_service(db: AsyncSession = Depends(get_db)) -> CoachService:
    return CoachService(db)

def get_school_service(db: AsyncSession = Depends(get_db)) -> SchoolService:
    return SchoolService(db)

class CoachResponse(BaseModel):
    id: int
    user_id: int
    school_id: int | None
    photo_url: str | None
    bio: str | None
    birth_date: datetime | None
    qualification: str | None
    experience_years: int
    specialization: str | None
    is_head_coach: bool
    achievements: str | None

    class Config:
        from_attributes = True

@router.get("/{coach_id}/page")
async def coach_detail_page(
    coach_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Страница профиля тренера"""
    coach_service = CoachService(db)
    school_service = SchoolService(db)
    
    coach = await coach_service.get_coach(coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    
    school = None
    if coach.school_id:
        school = await school_service.get_school(coach.school_id)
    
    return templates.TemplateResponse(
        "coach_detail.html",
        {
            "request": request,
            "coach": coach,
            "school": school,
            "now": datetime.now(timezone.utc)
        }
    )

@router.get("/{coach_id}", response_model=CoachResponse)
async def get_coach(
    coach_id: int,
    service: CoachService = Depends(get_coach_service),
):
    coach = await service.get_coach(coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    return coach

# ===== ЗАГРУЗКА АВАТАРА =====
from fastapi import UploadFile, File
from app.services.image_service import ImageService

@router.post("/{coach_id}/upload-avatar")
async def upload_coach_avatar(
    coach_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.COACH, UserRole.SCHOOL_REP])),
    db: AsyncSession = Depends(get_db),
):
    """Загрузить аватар тренера"""
    from app.services.coach_service import CoachService
    service = CoachService(db)
    
    coach = await service.get_coach(coach_id)
    if not coach:
        raise HTTPException(404, "Coach not found")
    
    if coach.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.SCHOOL_REP]:
        raise HTTPException(403, "Not authorized")
    
    url = await ImageService.save_image(file, "coaches", resize=(400, 400))
    await service.update_coach(coach_id, photo_url=url)
    
    return {"photo_url": url}

@router.post("/{coach_id}/upload-cover")
async def upload_coach_cover(
    coach_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.COACH, UserRole.SCHOOL_REP])),
    db: AsyncSession = Depends(get_db),
):
    """Загрузить обложку тренера"""
    from app.services.coach_service import CoachService
    service = CoachService(db)
    
    coach = await service.get_coach(coach_id)
    if not coach:
        raise HTTPException(404, "Coach not found")
    
    if coach.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.SCHOOL_REP]:
        raise HTTPException(403, "Not authorized")
    
    url = await ImageService.save_image(file, "coaches", resize=(1200, 400))
    await service.update_coach(coach_id, cover_url=url)
    
    return {"cover_url": url}
