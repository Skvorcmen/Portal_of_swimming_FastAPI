from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.services.coach_service import CoachService
from app.models import User, UserRole
from app.core.dependencies import require_role

router = APIRouter(prefix="/coach-profiles", tags=["coach-profiles"])


def get_coach_service(db: AsyncSession = Depends(get_db)) -> CoachService:
    return CoachService(db)


class CoachProfileCreate(BaseModel):
    user_id: int
    school_id: Optional[int] = None
    qualification: Optional[str] = None
    experience_years: int = 0
    specialization: Optional[str] = None
    is_head_coach: bool = False
    bio: Optional[str] = None
    achievements: Optional[str] = None
    photo_url: Optional[str] = None
    birth_date: Optional[datetime] = None


class CoachProfileResponse(BaseModel):
    id: int
    user_id: int
    school_id: Optional[int]
    qualification: Optional[str]
    experience_years: int
    specialization: Optional[str]
    is_head_coach: bool
    bio: Optional[str]
    achievements: Optional[str]
    photo_url: Optional[str]
    birth_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=CoachProfileResponse)
async def create_coach_profile(
    data: CoachProfileCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SCHOOL_REP])),
    service: CoachService = Depends(get_coach_service),
):
    """Создать профиль тренера"""
    return await service.create_coach_profile(**data.model_dump())
