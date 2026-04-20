from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.age_category_service import AgeCategoryService
from app.auth import get_current_active_user
from app.models import User, UserRole
from app.core.dependencies import require_role

router = APIRouter(prefix="/age-categories", tags=["age-categories"])


def get_age_category_service(db: AsyncSession = Depends(get_db)) -> AgeCategoryService:
    return AgeCategoryService(db)


# Схемы
class AgeCategoryCreate(BaseModel):
    competition_id: int
    name: str
    min_age: int
    max_age: int
    gender: str | None = None


class AgeCategoryUpdate(BaseModel):
    name: str | None = None
    min_age: int | None = None
    max_age: int | None = None
    gender: str | None = None


class AgeCategoryResponse(BaseModel):
    id: int
    competition_id: int
    name: str
    min_age: int
    max_age: int
    gender: str | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=AgeCategoryResponse)
async def create_age_category(
    category_data: AgeCategoryCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: AgeCategoryService = Depends(get_age_category_service),
):
    """Создать возрастную категорию (ADMIN, SECRETARY)"""
    if category_data.min_age >= category_data.max_age:
        raise HTTPException(status_code=400, detail="min_age must be less than max_age")

    category = await service.create_age_category(
        competition_id=category_data.competition_id,
        name=category_data.name,
        min_age=category_data.min_age,
        max_age=category_data.max_age,
        gender=category_data.gender,
    )
    return category


@router.get("/competition/{competition_id}", response_model=List[AgeCategoryResponse])
async def get_categories_by_competition(
    competition_id: int,
    service: AgeCategoryService = Depends(get_age_category_service),
):
    """Получить все возрастные категории для соревнования"""
    return await service.get_categories_by_competition(competition_id)


@router.get("/{category_id}", response_model=AgeCategoryResponse)
async def get_age_category(
    category_id: int,
    service: AgeCategoryService = Depends(get_age_category_service),
):
    """Получить возрастную категорию по ID"""
    category = await service.get_age_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Age category not found")
    return category


@router.put("/{category_id}", response_model=AgeCategoryResponse)
async def update_age_category(
    category_id: int,
    category_data: AgeCategoryUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: AgeCategoryService = Depends(get_age_category_service),
):
    """Обновить возрастную категорию (ADMIN, SECRETARY)"""
    update_data = {k: v for k, v in category_data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    category = await service.update_age_category(category_id, **update_data)
    if not category:
        raise HTTPException(status_code=404, detail="Age category not found")
    return category


@router.delete("/{category_id}")
async def delete_age_category(
    category_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: AgeCategoryService = Depends(get_age_category_service),
):
    """Удалить возрастную категорию (ADMIN, SECRETARY)"""
    deleted = await service.delete_age_category(category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Age category not found")
    return {"message": "Age category deleted successfully"}
