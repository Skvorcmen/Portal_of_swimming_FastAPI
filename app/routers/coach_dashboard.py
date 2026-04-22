from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.auth import get_current_active_user
from app.models import User, UserRole
from app.core.logging_config import logger

router = APIRouter(prefix="/coach", tags=["coach"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
async def coach_dashboard(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Панель управления тренера"""
    
    # Проверяем, что пользователь - тренер
    if current_user.role != UserRole.COACH:
        raise HTTPException(status_code=403, detail="Access denied. Coach only.")
    
    # Получаем профиль тренера
    result = await db.execute(
        text("""
            SELECT cp.*, s.name as school_name
            FROM coach_profiles cp
            LEFT JOIN schools s ON s.id = cp.school_id
            WHERE cp.user_id = :user_id
        """),
        {"user_id": current_user.id}
    )
    coach_profile = result.fetchone()
    
    if not coach_profile:
        # Создаем профиль тренера если нет
        result = await db.execute(
            text("""
                INSERT INTO coach_profiles (user_id, experience_years)
                VALUES (:user_id, 0)
                RETURNING id
            """),
            {"user_id": current_user.id}
        )
        await db.commit()
        coach_id = result.scalar()
    else:
        coach_id = coach_profile.id
    
    # Получаем список учеников
    students_result = await db.execute(
        text("""
            SELECT 
                u.id, u.full_name, u.email,
                a.birth_date, a.gender, a.rank,
                s.name as school_name,
                (
                    SELECT COUNT(*) 
                    FROM entries e 
                    JOIN heat_entries he ON he.entry_id = e.id 
                    WHERE e.athlete_id = a.id AND he.result_time IS NOT NULL
                ) as races_count,
                (
                    SELECT MIN(he.result_time) 
                    FROM entries e 
                    JOIN heat_entries he ON he.entry_id = e.id 
                    WHERE e.athlete_id = a.id AND he.result_time IS NOT NULL
                ) as best_time
            FROM athlete_profiles a
            JOIN "user" u ON u.id = a.user_id
            LEFT JOIN schools s ON s.id = a.school_id
            WHERE a.coach_id = :coach_id
            ORDER BY u.full_name
        """),
        {"coach_id": coach_id}
    )
    students = students_result.fetchall()
    
    # Получаем статистику
    stats_result = await db.execute(
        text("""
            SELECT 
                COUNT(DISTINCT a.id) as total_students,
                COUNT(DISTINCT e.competition_id) as total_competitions,
                COUNT(he.id) as total_races,
                AVG(he.place) as avg_place
            FROM coach_profiles cp
            JOIN athlete_profiles a ON a.coach_id = cp.id
            LEFT JOIN entries e ON e.athlete_id = a.id
            LEFT JOIN heat_entries he ON he.entry_id = e.id
            WHERE cp.id = :coach_id
        """),
        {"coach_id": coach_id}
    )
    stats = stats_result.fetchone()
    
    return templates.TemplateResponse(
        "coach_dashboard.html",
        {
            "request": request,
            "coach": coach_profile,
            "students": students,
            "stats": stats,
            "current_user": current_user
        }
    )


@router.get("/student/{student_id}")
async def student_details(
    student_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Детали ученика для тренера"""
    
    if current_user.role != UserRole.COACH:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Получаем данные ученика
    result = await db.execute(
        text("""
            SELECT 
                u.id, u.full_name, u.email, u.username,
                a.birth_date, a.gender, a.rank,
                s.name as school_name
            FROM athlete_profiles a
            JOIN "user" u ON u.id = a.user_id
            LEFT JOIN schools s ON s.id = a.school_id
            WHERE a.id = :student_id
        """),
        {"student_id": student_id}
    )
    student = result.fetchone()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Получаем результаты ученика
    results = await db.execute(
        text("""
            SELECT 
                c.name as competition_name,
                c.start_date,
                se.name as event_name,
                se.distance,
                se.stroke,
                he.result_time,
                he.place
            FROM entries e
            JOIN swim_events se ON se.id = e.swim_event_id
            JOIN competitions c ON c.id = se.competition_id
            JOIN heat_entries he ON he.entry_id = e.id
            WHERE e.athlete_id = :student_id AND he.result_time IS NOT NULL
            ORDER BY c.start_date DESC
            LIMIT 20
        """),
        {"student_id": student_id}
    )
    
    return templates.TemplateResponse(
        "coach_student_detail.html",
        {
            "request": request,
            "student": student,
            "results": results.fetchall()
        }
    )
