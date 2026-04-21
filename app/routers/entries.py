from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from fastapi import UploadFile, File
from app.database import get_db
from app.services.entry_service import EntryService
from app.models import User, UserRole
from app.core.dependencies import require_role
from app.auth import get_current_active_user
from fastapi.responses import StreamingResponse
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from app.services.competition_service import CompetitionService
from datetime import datetime


def get_competition_service(db: AsyncSession = Depends(get_db)) -> CompetitionService:
    return CompetitionService(db)


router = APIRouter(prefix="/entries", tags=["entries"])


def get_entry_service(db: AsyncSession = Depends(get_db)) -> EntryService:
    return EntryService(db)


# Схемы
class EntryCreate(BaseModel):
    competition_id: int
    swim_event_id: int
    athlete_id: int
    entry_time: float | None = None
    status: str = "pending"


class EntryUpdate(BaseModel):
    status: str | None = None
    entry_time: float | None = None


class EntryResponse(BaseModel):
    id: int
    competition_id: int
    swim_event_id: int
    athlete_id: int
    status: str
    entry_time: float | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=EntryResponse)
async def create_entry(
    data: EntryCreate,
    current_user: User = Depends(
        require_role([UserRole.ADMIN, UserRole.SECRETARY, UserRole.COACH])
    ),
    service: EntryService = Depends(get_entry_service),
):
    """Создать заявку (ADMIN, SECRETARY, COACH)"""
    entry = await service.create_entry(**data.model_dump())
    return entry


@router.get("/competition/{competition_id}", response_model=List[EntryResponse])
async def get_entries_by_competition(
    competition_id: int,
    service: EntryService = Depends(get_entry_service),
):
    """Получить заявки для соревнования"""
    return await service.get_entries_by_competition(competition_id)


@router.get("/swim-event/{swim_event_id}", response_model=List[EntryResponse])
async def get_entries_by_swim_event(
    swim_event_id: int,
    service: EntryService = Depends(get_entry_service),
):
    """Получить заявки для дистанции"""
    return await service.get_entries_by_swim_event(swim_event_id)


@router.get("/athlete/{athlete_id}", response_model=List[EntryResponse])
async def get_entries_by_athlete(
    athlete_id: int,
    current_user: User = Depends(
        require_role(
            [UserRole.ADMIN, UserRole.SECRETARY, UserRole.COACH, UserRole.ATHLETE]
        )
    ),
    service: EntryService = Depends(get_entry_service),
):
    """Получить заявки спортсмена (ADMIN, SECRETARY, COACH, ATHLETE)"""
    # Простая проверка: если пользователь не админ и не секретарь,
    # он может видеть только свои заявки (нужно связать athlete_id с user_id)
    return await service.get_entries_by_athlete(athlete_id)


@router.get("/{entry_id}", response_model=EntryResponse)
async def get_entry(
    entry_id: int,
    service: EntryService = Depends(get_entry_service),
):
    entry = await service.get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.put("/{entry_id}", response_model=EntryResponse)
async def update_entry(
    entry_id: int,
    data: EntryUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: EntryService = Depends(get_entry_service),
):
    """Обновить заявку (ADMIN, SECRETARY)"""
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    entry = await service.update_entry_status(entry_id, update_data.get("status"))
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.delete("/{entry_id}")
async def delete_entry(
    entry_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: EntryService = Depends(get_entry_service),
):
    """Удалить заявку (ADMIN, SECRETARY)"""
    deleted = await service.delete_entry(entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"message": "Entry deleted successfully"}


@router.get("/template/{competition_id}")
async def download_entry_template(
    competition_id: int,
    current_user: User = Depends(
        require_role([UserRole.ADMIN, UserRole.SECRETARY, UserRole.COACH])
    ),
    entry_service: EntryService = Depends(get_entry_service),
    competition_service: CompetitionService = Depends(get_competition_service),
):
    competition = await competition_service.get_competition(competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    output = await entry_service.generate_excel_template(competition_id)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=entries_template_{competition_id}.xlsx"
        },
    )


@router.post("/upload/{competition_id}")
async def upload_entries_excel(
    competition_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(
        require_role([UserRole.ADMIN, UserRole.SECRETARY, UserRole.COACH])
    ),
    entry_service: EntryService = Depends(get_entry_service),
    competition_service: CompetitionService = Depends(get_competition_service),
):
    # Проверяем, существует ли соревнование
    competition = await competition_service.get_competition(competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    # Проверяем расширение файла
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400, detail="File must be Excel format (.xlsx or .xls)"
        )

    # Читаем файл и передаём в сервис
    contents = await file.read()
    result = await entry_service.import_from_excel(competition_id, contents)

    if result.get("errors"):
        raise HTTPException(status_code=400, detail=result)

    return result
