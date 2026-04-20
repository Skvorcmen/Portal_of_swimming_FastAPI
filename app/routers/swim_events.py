from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.swim_event_service import SwimEventService
from app.models import User, UserRole
from app.core.dependencies import require_role

router = APIRouter(prefix="/swim-events", tags=["swim-events"])


def get_swim_event_service(db: AsyncSession = Depends(get_db)) -> SwimEventService:
    return SwimEventService(db)


class SwimEventCreate(BaseModel):
    competition_id: int
    name: str
    distance: int
    stroke: str
    gender: str | None = None
    is_relay: bool = False
    order: int = 0


class SwimEventUpdate(BaseModel):
    name: str | None = None
    distance: int | None = None
    stroke: str | None = None
    gender: str | None = None
    is_relay: bool | None = None
    order: int | None = None


class SwimEventResponse(BaseModel):
    id: int
    competition_id: int
    name: str
    distance: int
    stroke: str
    gender: str | None
    is_relay: bool
    order: int
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=SwimEventResponse)
async def create_swim_event(
    data: SwimEventCreate,
    _: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: SwimEventService = Depends(get_swim_event_service),
):
    return await service.create_swim_event(**data.model_dump())


@router.get("/competition/{competition_id}", response_model=List[SwimEventResponse])
async def get_swim_events_by_competition(
    competition_id: int,
    service: SwimEventService = Depends(get_swim_event_service),
):
    return await service.get_by_competition(competition_id)


@router.get("/{event_id}", response_model=SwimEventResponse)
async def get_swim_event(
    event_id: int,
    service: SwimEventService = Depends(get_swim_event_service),
):
    event = await service.get_swim_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Swim event not found")
    return event


@router.put("/{event_id}", response_model=SwimEventResponse)
async def update_swim_event(
    event_id: int,
    data: SwimEventUpdate,
    _: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: SwimEventService = Depends(get_swim_event_service),
):
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    event = await service.update_swim_event(event_id, **update_data)
    if not event:
        raise HTTPException(status_code=404, detail="Swim event not found")
    return event


@router.delete("/{event_id}")
async def delete_swim_event(
    event_id: int,
    _: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: SwimEventService = Depends(get_swim_event_service),
):
    deleted = await service.delete_swim_event(event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Swim event not found")
    return {"message": "Swim event deleted successfully"}
