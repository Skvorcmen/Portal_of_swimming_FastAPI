from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.heat_service import HeatService
from app.models import User, UserRole
from app.core.dependencies import require_role
from fastapi.responses import StreamingResponse
import asyncio
import json

router = APIRouter(prefix="/heats", tags=["heats"])


def get_heat_service(db: AsyncSession = Depends(get_db)) -> HeatService:
    return HeatService(db)


class HeatResponse(BaseModel):
    id: int
    swim_event_id: int
    heat_number: int
    lane_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class HeatEntryResponse(BaseModel):
    id: int
    heat_id: int
    entry_id: int
    lane: int
    result_time: float | None
    place: int | None

    class Config:
        from_attributes = True


class ResultInput(BaseModel):
    result_time: float


@router.post("/generate/{swim_event_id}")
async def generate_heats(
    swim_event_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: HeatService = Depends(get_heat_service),
):
    """Сгенерировать заплывы для дистанции"""
    result = await service.generate_heats(swim_event_id)
    return result


@router.get("/swim-event/{swim_event_id}", response_model=List[HeatResponse])
async def get_heats_by_swim_event(
    swim_event_id: int,
    service: HeatService = Depends(get_heat_service),
):
    return await service.get_heats_by_swim_event(swim_event_id)


@router.post("/entry/{heat_entry_id}/result")
async def set_result(
    heat_entry_id: int,
    data: ResultInput,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: HeatService = Depends(get_heat_service),
):
    """Ввести результат для участника (ADMIN, SECRETARY)"""
    try:
        heat_entry = await service.enter_result(heat_entry_id, data.result_time)
        return {"message": "Result saved", "heat_entry": heat_entry}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/heat/{heat_id}/complete")
async def complete_heat(
    heat_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: HeatService = Depends(get_heat_service),
):
    """Завершить заплыв и рассчитать места (ADMIN, SECRETARY)"""
    try:
        heat = await service.complete_heat(heat_id)
        return {"message": "Heat completed", "heat": heat}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/heat/{heat_id}/results")
async def get_heat_results(
    heat_id: int,
    service: HeatService = Depends(get_heat_service),
):
    entries = await service.get_heat_results(heat_id)
    entries_sorted = sorted(entries, key=lambda e: e.place if e.place else 999)
    return [
        {
            "lane": e.lane,
            "entry_id": e.entry_id,
            "result_time": e.result_time,
            "place": e.place,
        }
        for e in entries_sorted
    ]


@router.get("/live/{competition_id}/events")
async def live_results_stream(
    competition_id: int,
    service: HeatService = Depends(get_heat_service),
):
    """SSE поток для live-таблицы результатов"""

    async def event_generator():
        while True:
            # Получаем актуальные результаты из сервиса
            results = await service.get_live_results(competition_id)

            # Отправляем событие с данными
            yield f"data: {json.dumps(results, default=str)}\n\n"

            await asyncio.sleep(2)  # Обновление каждые 2 секунды

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
