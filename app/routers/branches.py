from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Branch, School

router = APIRouter(prefix="/branches", tags=["branches"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/{branch_id}/page")
async def branch_detail_page(
    branch_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # Получаем филиал
    result = await db.execute(
        select(Branch).where(Branch.id == branch_id)
    )
    branch = result.scalar_one_or_none()
    
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    # Получаем школу
    school_result = await db.execute(
        select(School).where(School.id == branch.school_id)
    )
    school = school_result.scalar_one_or_none()
    
    return templates.TemplateResponse(
        "branch_detail.html",
        {
            "request": request,
            "branch": branch,
            "school": school
        }
    )

@router.get("/{branch_id}/coaches")
async def get_branch_coaches(
    branch_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Получить тренеров филиала (API)"""
    from sqlalchemy.orm import selectinload
    from app.models import CoachProfile, User
    
    result = await db.execute(
        select(CoachProfile)
        .options(selectinload(CoachProfile.user))
        .where(CoachProfile.branch_id == branch_id)
    )
    coaches = result.scalars().all()
    
    return [
        {
            "id": coach.id,
            "full_name": coach.user.full_name if coach.user else "Unknown",
            "qualification": coach.qualification,
            "experience_years": coach.experience_years,
            "specialization": coach.specialization,
            "is_head_coach": coach.is_head_coach,
            "photo_url": coach.photo_url
        }
        for coach in coaches
    ]
