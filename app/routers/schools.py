from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.school_service import SchoolService
from app.services.coach_service import CoachService
from app.models import User, UserRole
from app.core.dependencies import require_role

router = APIRouter(prefix="/schools", tags=["schools"])
templates = Jinja2Templates(directory="app/templates")


def get_school_service(db: AsyncSession = Depends(get_db)) -> SchoolService:
    return SchoolService(db)


def get_coach_service(db: AsyncSession = Depends(get_db)) -> CoachService:
    return CoachService(db)


class SchoolCreate(BaseModel):
    name: str
    city: str
    address: str
    description: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    logo_url: str | None = None
    cover_url: str | None = None
    founded_year: int | None = None


class SchoolUpdate(BaseModel):
    name: str | None = None
    city: str | None = None
    address: str | None = None
    description: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    logo_url: str | None = None
    cover_url: str | None = None
    founded_year: int | None = None


class SchoolResponse(BaseModel):
    id: int
    name: str
    city: str
    address: str
    description: str | None
    phone: str | None
    email: str | None
    website: str | None
    logo_url: str | None
    cover_url: str | None
    founded_year: int | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Страница со списком школ
@router.get("/page")
async def schools_page(request: Request):
    return templates.TemplateResponse("schools_list.html", {"request": request})


# API для поиска школ
@router.get("/search")
async def search_schools(
    request: Request,
    name: str = "",
    city: str = "",
    page: int = 1,
    service: SchoolService = Depends(get_school_service),
):
    result = await service.search_schools(name, city, page)
    return templates.TemplateResponse(
        "partials/school_items.html",
        {
            "request": request,
            "schools": result["items"],
            "page": page,
            "total": result["total"],
            "pages": result["pages"],
            "name": name,
            "city": city,
        },
    )


# Страница деталей школы
@router.get("/{school_id}/page")
async def school_detail_page(
    school_id: int,
    request: Request,
    school_service: SchoolService = Depends(get_school_service),
    coach_service: CoachService = Depends(get_coach_service),
):
    school = await school_service.get_school(school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    coaches = await coach_service.get_coaches_by_school(school_id)

    return templates.TemplateResponse(
        "school_detail.html", {"request": request, "school": school, "coaches": coaches}
    )


# API для получения школы (JSON)
@router.get("/{school_id}/page")
async def school_detail_page(
    school_id: int,
    request: Request,
    school_service: SchoolService = Depends(get_school_service),
    coach_service: CoachService = Depends(get_coach_service),
):
    school = await school_service.get_school(school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")

    coaches = await coach_service.get_coaches_by_school(school_id)

    return templates.TemplateResponse(
        "school_detail.html", {"request": request, "school": school, "coaches": coaches}
    )


# Создание школы (только ADMIN)
@router.post("/", response_model=SchoolResponse)
async def create_school(
    data: SchoolCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SCHOOL_REP])),
    service: SchoolService = Depends(get_school_service),
):
    return await service.create_school(**data.model_dump())


# Обновление школы
@router.put("/{school_id}", response_model=SchoolResponse)
async def update_school(
    school_id: int,
    data: SchoolUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SCHOOL_REP])),
    service: SchoolService = Depends(get_school_service),
):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    school = await service.update_school(school_id, **update_data)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school


# Удаление школы
@router.delete("/{school_id}")
async def delete_school(
    school_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN])),
    service: SchoolService = Depends(get_school_service),
):
    deleted = await service.delete_school(school_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="School not found")
    return {"message": "School deleted successfully"}
