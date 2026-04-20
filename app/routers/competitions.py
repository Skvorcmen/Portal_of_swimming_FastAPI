from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.competition_service import CompetitionService
from app.auth import get_current_active_user
from app.models import User
from app.core.dependencies import require_role
from app.models import UserRole

router = APIRouter(prefix="/competitions", tags=["competitions"])


def get_competition_service(db: AsyncSession = Depends(get_db)) -> CompetitionService:
    return CompetitionService(db)


# Схемы для запросов/ответов
class CompetitionCreate(BaseModel):
    name: str
    description: str | None = None
    start_date: datetime
    end_date: datetime
    venue: str | None = None
    city: str | None = None
    status: str = "draft"
    max_participants: int = 0


class CompetitionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    venue: str | None = None
    city: str | None = None
    status: str | None = None
    max_participants: int | None = None


class CompetitionResponse(BaseModel):
    id: int
    name: str
    description: str | None
    start_date: datetime
    end_date: datetime
    venue: str | None
    city: str | None
    status: str
    max_participants: int
    created_by: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=CompetitionResponse)
async def create_competition(
    competition_data: CompetitionCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: CompetitionService = Depends(get_competition_service),
):
    """Создать новое соревнование (только ADMIN, SECRETARY)"""
    competition = await service.create_competition(
        name=competition_data.name,
        description=competition_data.description,
        start_date=competition_data.start_date,
        end_date=competition_data.end_date,
        venue=competition_data.venue,
        city=competition_data.city,
        status=competition_data.status,
        max_participants=competition_data.max_participants,
        created_by=current_user.id,
    )
    return competition


@router.get("/", response_model=List[CompetitionResponse])
async def get_all_competitions(
    skip: int = 0,
    limit: int = 100,
    service: CompetitionService = Depends(get_competition_service),
):
    """Получить список всех соревнований"""
    return await service.get_all_competitions(skip, limit)


@router.get("/active", response_model=List[CompetitionResponse])
async def get_active_competitions(
    service: CompetitionService = Depends(get_competition_service),
):
    """Получить список активных соревнований"""
    return await service.get_active_competitions()


@router.get("/upcoming", response_model=List[CompetitionResponse])
async def get_upcoming_competitions(
    service: CompetitionService = Depends(get_competition_service),
):
    """Получить список предстоящих соревнований"""
    return await service.get_upcoming_competitions()


@router.get("/{competition_id}", response_model=CompetitionResponse)
async def get_competition(
    competition_id: int,
    service: CompetitionService = Depends(get_competition_service),
):
    """Получить соревнование по ID"""
    competition = await service.get_competition(competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    return competition


@router.put("/{competition_id}", response_model=CompetitionResponse)
async def update_competition(
    competition_id: int,
    competition_data: CompetitionUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: CompetitionService = Depends(get_competition_service),
):
    """Обновить соревнование (только ADMIN, SECRETARY)"""
    # Убираем None значения
    update_data = {
        k: v for k, v in competition_data.model_dump().items() if v is not None
    }
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    competition = await service.update_competition(competition_id, **update_data)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    return competition


@router.delete("/{competition_id}")
async def delete_competition(
    competition_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: CompetitionService = Depends(get_competition_service),
):
    """Удалить соревнование (только ADMIN, SECRETARY)"""
    deleted = await service.delete_competition(competition_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Competition not found")
    return {"message": "Competition deleted successfully"}
