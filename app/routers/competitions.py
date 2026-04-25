from sqlalchemy import select
from app.models import Competition, CompetitionSubscription


from app.auth import get_current_user_optional_cookie

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from datetime import datetime
from app.core.cache import cached, delete_cache, clear_cache_pattern
from app.database import get_db
from app.services.competition_service import CompetitionService
from app.auth import get_current_active_user
from app.models import User
from app.core.dependencies import require_role
from app.models import UserRole
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse
from urllib.parse import unquote
from fastapi.responses import StreamingResponse
from app.services.pdf_service import PDFService

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/competitions", tags=["competitions"])



# ===== ЭНДПОИНТЫ ПОДПИСКИ =====
@router.post("/{competition_id}/subscribe")
async def toggle_subscription(
    competition_id: int,
    current_user: User = Depends(get_current_user_optional_cookie),
    db: AsyncSession = Depends(get_db),
):
    """Подписаться/отписаться от результатов соревнования"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    competition = await db.execute(
        select(Competition).where(Competition.id == competition_id)
    )
    competition = competition.scalar_one_or_none()
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    
    result = await db.execute(
        select(CompetitionSubscription).where(
            CompetitionSubscription.user_id == current_user.id,
            CompetitionSubscription.competition_id == competition_id
        )
    )
    subscription = result.scalar_one_or_none()
    
    if subscription:
        await db.delete(subscription)
        await db.commit()
        return {"subscribed": False}
    else:
        new_subscription = CompetitionSubscription(
            user_id=current_user.id,
            competition_id=competition_id
        )
        db.add(new_subscription)
        await db.commit()
        return {"subscribed": True}


@router.get("/{competition_id}/subscription-status")
async def get_subscription_status(
    competition_id: int,
    current_user: User = Depends(get_current_user_optional_cookie),
    db: AsyncSession = Depends(get_db),
):
    """Проверить статус подписки"""
    if not current_user:
        return {"subscribed": False}
    
    result = await db.execute(
        select(CompetitionSubscription).where(
            CompetitionSubscription.user_id == current_user.id,
            CompetitionSubscription.competition_id == competition_id
        )
    )
    subscription = result.scalar_one_or_none()
    return {"subscribed": subscription is not None}


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


@router.get("/page")
async def competitions_page(
    request: Request,
    service: CompetitionService = Depends(get_competition_service),
):
    competitions = await service.get_all_competitions()
    return templates.TemplateResponse(
        "competitions_list.html", {"request": request, "competitions": competitions}
    )


@router.get("/search")
async def search_competitions(
    request: Request,
    name: str = "",
    city: str = "",
    status: str = "",
    page: int = 1,
    service: CompetitionService = Depends(get_competition_service),
):
    name = unquote(name)
    city = unquote(city)
    status = unquote(status)

    result = await service.search_competitions(name, city, status, page)
    return templates.TemplateResponse(
        "partials/competition_items.html",
        {
            "request": request,
            "competitions": result["items"],
            "page": page,
            "total": result["total"],
            "pages": result["pages"],
        },
    )


@router.get("/active", response_model=List[CompetitionResponse])
async def get_active_competitions(
    service: CompetitionService = Depends(get_competition_service),
):
    return await service.get_active_competitions()


@router.get("/upcoming", response_model=List[CompetitionResponse])
async def get_upcoming_competitions(
    service: CompetitionService = Depends(get_competition_service),
):
    return await service.get_upcoming_competitions()


@router.post("/", response_model=CompetitionResponse)
async def create_competition(
    competition_data: CompetitionCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: CompetitionService = Depends(get_competition_service),
):
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
@cached(expire=60, key_prefix="competitions_list")
async def get_all_competitions(
    skip: int = 0,
    limit: int = 100,
    service: CompetitionService = Depends(get_competition_service),
):
    return await service.get_all_competitions(skip, limit)


@router.get("/{competition_id}", response_model=CompetitionResponse)
@cached(expire=300, key_prefix="competition_detail")
async def get_competition(
    competition_id: int,
    service: CompetitionService = Depends(get_competition_service),
):
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
    update_data = {
        k: v for k, v in competition_data.model_dump().items() if v is not None
    }
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    competition = await service.update_competition(competition_id, **update_data)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    # Очищаем кэш
    await clear_cache_pattern("competition_list*")
    await clear_cache_pattern(f"competition_detail:{competition_id}*")

    return competition


@router.delete("/{competition_id}")
async def delete_competition(
    competition_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SECRETARY])),
    service: CompetitionService = Depends(get_competition_service),
):
    deleted = await service.delete_competition(competition_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Competition not found")
    return {"message": "Competition deleted successfully"}


@router.get("/{competition_id}/page")
async def competition_detail_page(
    competition_id: int,
    request: Request,
    service: CompetitionService = Depends(get_competition_service),
):
    competition = await service.get_competition(competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    return templates.TemplateResponse(
        "competition_detail.html", {"request": request, "competition": competition}
    )


@router.get("/{competition_id}/start-list.pdf")
async def download_start_list(
    competition_id: int,
    db: AsyncSession = Depends(get_db),
):
    pdf_buffer = await PDFService.generate_start_list(competition_id, db)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=start_list_{competition_id}.pdf"
        },
    )


@router.get("/{competition_id}/results.pdf")
async def download_results_protocol(
    competition_id: int,
    db: AsyncSession = Depends(get_db),
):
    pdf_buffer = await PDFService.generate_results_protocol(competition_id, db)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=results_{competition_id}.pdf"
        },
    )




@router.get("/test-cache")
@cached(expire=30, key_prefix="test")
async def test_cache():
    import time
    return {"timestamp": time.time(), "message": "Cached response"}


#@router.get("/{competition_id}/results.csv")
#async def download_results_csv(
#    competition_id: int,
#    db: AsyncSession = Depends(get_db),
#):
#    """Скачать результаты соревнования в CSV"""
#    from app.services.csv_service import CSVService
#    
#    csv_buffer = await CSVService.export_competition_results(competition_id, db)
#    return StreamingResponse(
#        csv_buffer,
#        media_type="text/csv",
#        headers={
#            "Content-Disposition": f"attachment; filename=results_{competition_id}.csv"
#        },
#
@router.get("/{competition_id}/subscription-status")
#async def view_competition_rules(
#    competition_id: int,
#    db: AsyncSession = Depends(get_db),
#):
#    """Просмотр положения о соревновании в браузере"""
#    pdf_buffer = await PDFService.generate_competition_rules(competition_id, db)
#    return StreamingResponse(
#        pdf_buffer,
#        media_type="application/pdf",
#        headers={
#            "Content-Disposition": f"inline; filename=rules_{competition_id}.pdf"
#        },

# ===== ЭНДПОИНТЫ ДЛЯ ПРОСМОТРА В БРАУЗЕРЕ =====

@router.get("/{competition_id}/start-list/view")
async def view_start_list(
    competition_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Просмотр стартового протокола в браузере"""
    pdf_buffer = await PDFService.generate_start_list(competition_id, db)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=start_list_{competition_id}.pdf"},
    )

@router.get("/{competition_id}/results/view")
async def view_results_protocol(
    competition_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Просмотр итогового протокола в браузере"""
    pdf_buffer = await PDFService.generate_results_protocol(competition_id, db)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=results_{competition_id}.pdf"},
    )

@router.get("/{competition_id}/rules/view")
async def view_competition_rules(
    competition_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Просмотр положения о соревновании в браузере"""
    pdf_buffer = await PDFService.generate_competition_rules(competition_id, db)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=rules_{competition_id}.pdf"},
    )


@router.get("/{competition_id}/subscription-status")
async def get_subscription_status(
    competition_id: int,
    current_user: User = Depends(get_current_user_optional_cookie),
    db: AsyncSession = Depends(get_db),
):
    """Проверить статус подписки"""
    if not current_user:
        return {"subscribed": False}
    
    result = await db.execute(
        select(CompetitionSubscription).where(
            CompetitionSubscription.user_id == current_user.id,
            CompetitionSubscription.competition_id == competition_id
        )
    )
    subscription = result.scalar_one_or_none()
    return {"subscribed": subscription is not None}

@router.get("/{competition_id}/subscription-status")
async def get_subscription_status(
    competition_id: int,
    current_user: User = Depends(get_current_user_optional_cookie),
    db: AsyncSession = Depends(get_db),
):
    """Проверить статус подписки"""
    if not current_user:
        return {"subscribed": False}
    
    result = await db.execute(
        select(CompetitionSubscription).where(
            CompetitionSubscription.user_id == current_user.id,
            CompetitionSubscription.competition_id == competition_id
        )
    )
    subscription = result.scalar_one_or_none()
    return {"subscribed": subscription is not None}
