from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime

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


# Страница деталей тренера
@router.get("/{coach_id}/page")
async def coach_detail_page(
    coach_id: int,
    request: Request,
    coach_service: CoachService = Depends(get_coach_service),
    school_service: SchoolService = Depends(get_school_service),
):
    coach = await coach_service.get_coach(coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    
    school = None
    if coach.school_id:
        school = await school_service.get_school(coach.school_id)
    
    return templates.TemplateResponse("coach_detail.html", {
        "request": request,
        "coach": coach,
        "school": school
    })


# API для получения тренера
@router.get("/{coach_id}", response_model=CoachResponse)
async def get_coach(
    coach_id: int,
    service: CoachService = Depends(get_coach_service),
):
    coach = await service.get_coach(coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    return coach
