from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime, date

from app.database import get_db
from app.services.athlete_service import AthleteService
from app.services.school_service import SchoolService
from app.services.coach_service import CoachService
from app.models import User, UserRole
from app.core.dependencies import require_role
from app.auth import get_current_user_optional_cookie, get_current_active_user

router = APIRouter(prefix="/athletes", tags=["athletes"])
templates = Jinja2Templates(directory="app/templates")

def get_athlete_service(db: AsyncSession = Depends(get_db)) -> AthleteService:
    return AthleteService(db)

def get_school_service(db: AsyncSession = Depends(get_db)) -> SchoolService:
    return SchoolService(db)

def get_coach_service(db: AsyncSession = Depends(get_db)) -> CoachService:
    return CoachService(db)

class PersonalBestCreate(BaseModel):
    distance: int
    stroke: str
    time_seconds: float
    set_date: str | None = None

class PersonalBestResponse(BaseModel):
    id: int
    athlete_id: int
    distance: int
    stroke: str
    time_seconds: float
    set_at: datetime
    set_date: str | None = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat() if v else None,
        }

@router.post("/my/personal-bests", response_model=PersonalBestResponse)
async def add_my_personal_best(
    data: PersonalBestCreate,
    current_user: User = Depends(get_current_user_optional_cookie),
    service: AthleteService = Depends(get_athlete_service),
):
    """Добавить личный рекорд для текущего пользователя-спортсмена"""
    if not current_user or current_user.role != UserRole.ATHLETE:
        raise HTTPException(status_code=401, detail="Not authenticated or not athlete")
    
    athlete = await service.get_athlete_by_user_id(current_user.id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete profile not found")
    
    pb = await service.add_personal_best(
        athlete_id=athlete.id,
        distance=data.distance,
        stroke=data.stroke,
        time_seconds=data.time_seconds,
        set_date=data.set_date,
    )
    if pb.set_date and not isinstance(pb.set_date, str):
        pb.set_date = pb.set_date.isoformat()
    return pb

@router.get("/my/personal-bests", response_model=List[PersonalBestResponse])
async def get_my_personal_bests(
    current_user: User = Depends(get_current_user_optional_cookie),
    service: AthleteService = Depends(get_athlete_service),
):
    """Получить личные рекорды текущего пользователя-спортсмена"""
    if not current_user or current_user.role != UserRole.ATHLETE:
        raise HTTPException(status_code=401, detail="Not authenticated or not athlete")
    
    athlete = await service.get_athlete_by_user_id(current_user.id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete profile not found")
    
    pbs = await service.get_personal_bests(athlete.id)
    return pbs

@router.delete("/personal-bests/{pb_id}")
async def delete_personal_best(
    pb_id: int,
    current_user: User = Depends(get_current_user_optional_cookie),
    service: AthleteService = Depends(get_athlete_service),
):
    """Удалить личный рекорд"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    pb = await service.get_personal_best(pb_id)
    if not pb:
        raise HTTPException(status_code=404, detail="Personal best not found")
    
    athlete = await service.get_athlete(pb.athlete_id)
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    if athlete.user_id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.COACH]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this record")
    
    deleted = await service.delete_personal_best(pb_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Personal best not found")
    return {"message": "Personal best deleted successfully"}

class PersonalBestResponse(BaseModel):
    id: int
    athlete_id: int
    distance: int
    stroke: str
    time_seconds: float
    set_at: datetime
    set_date: str | None = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat() if v else None,
        }
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat() if v else None,
        }

@router.get("/my/profile-data")
async def get_my_profile_data(
    current_user: User = Depends(get_current_user_optional_cookie),
    db: AsyncSession = Depends(get_db),
):
    """Получить данные профиля спортсмена"""
    if not current_user or current_user.role != UserRole.ATHLETE:
        raise HTTPException(status_code=401, detail="Not authenticated or not athlete")
    
    from sqlalchemy import select
    from app.models import AthleteProfile, School, CoachProfile, User
    
    result = await db.execute(
        select(AthleteProfile).where(AthleteProfile.user_id == current_user.id)
    )
    athlete = result.scalar_one_or_none()
    
    if not athlete:
        return {
            "birth_date": None,
            "gender": None,
            "rank": None,
            "school_name": None,
            "coach_name": None
        }
    
    # Получаем школу
    school_name = None
    if athlete.school_id:
        school_result = await db.execute(select(School).where(School.id == athlete.school_id))
        school = school_result.scalar_one_or_none()
        school_name = school.name if school else None
    
    # Получаем тренера
    coach_name = None
    if athlete.coach_id:
        coach_result = await db.execute(
            select(CoachProfile).where(CoachProfile.id == athlete.coach_id)
        )
        coach = coach_result.scalar_one_or_none()
        if coach:
            user_result = await db.execute(select(User).where(User.id == coach.user_id))
            coach_user = user_result.scalar_one_or_none()
            coach_name = coach_user.full_name if coach_user else None
    
    return {
        "birth_date": athlete.birth_date.isoformat() if athlete.birth_date else None,
        "gender": athlete.gender,
        "rank": athlete.rank,
        "school_name": school_name,
        "coach_name": coach_name
    }

@router.put("/my/profile")
async def update_my_profile(
    data: dict,
    current_user: User = Depends(get_current_user_optional_cookie),
    db: AsyncSession = Depends(get_db),
):
    """Обновить данные профиля спортсмена"""
    if not current_user or current_user.role != UserRole.ATHLETE:
        raise HTTPException(status_code=401, detail="Not authenticated or not athlete")
    
    from sqlalchemy import select
    from app.models import AthleteProfile
    
    result = await db.execute(
        select(AthleteProfile).where(AthleteProfile.user_id == current_user.id)
    )
    athlete = result.scalar_one_or_none()
    
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete profile not found")
    
    # Обновляем поля
    if 'birth_date' in data:
        athlete.birth_date = data['birth_date']
    if 'gender' in data:
        athlete.gender = data['gender']
    if 'rank' in data:
        athlete.rank = data['rank']
    
    await db.commit()
    return {"message": "Profile updated"}
