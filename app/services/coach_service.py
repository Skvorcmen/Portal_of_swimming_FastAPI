from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
from app.repositories.coach_repository import CoachRepository
from app.repositories.school_repository import SchoolRepository
from app.models import CoachProfile
from fastapi import HTTPException, status


class CoachService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CoachRepository(session)
        self.school_repo = SchoolRepository(session)

    async def get_coach(self, coach_id: int) -> Optional[CoachProfile]:
        return await self.repo.get_by_id(coach_id)

    async def get_coaches_by_school(self, school_id: int) -> List[CoachProfile]:
        return await self.repo.get_by_school(school_id)

    async def search_coaches(self, name: str = "", school_id: int = None) -> List[CoachProfile]:
        return await self.repo.search(name, school_id)

    async def create_coach_profile(
        self,
        user_id: int,
        school_id: int = None,
        qualification: str = None,
        experience_years: int = 0,
        specialization: str = None,
        is_head_coach: bool = False,
        bio: str = None,
        achievements: str = None,
        photo_url: str = None,
        birth_date: datetime = None,
    ) -> CoachProfile:
        # Проверяем, существует ли школа
        if school_id:
            school = await self.school_repo.get_by_id(school_id)
            if not school:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"School with id {school_id} not found"
                )
        
        return await self.repo.create(
            user_id=user_id,
            school_id=school_id,
            qualification=qualification,
            experience_years=experience_years,
            specialization=specialization,
            is_head_coach=is_head_coach,
            bio=bio,
            achievements=achievements,
            photo_url=photo_url,
            birth_date=birth_date,
        )

    async def get_coach_athletes(self, coach_id: int) -> List:
        """Получить всех учеников тренера"""
        from sqlalchemy import select
        from app.models import AthleteProfile, User
        
        result = await self.session.execute(
            select(AthleteProfile)
            .options(selectinload(AthleteProfile.user))
            .where(AthleteProfile.coach_id == coach_id)
        )
        return result.scalars().all()

    async def update_coach(self, coach_id: int, **kwargs) -> Optional[CoachProfile]:
        """Обновить данные тренера"""
        return await self.repo.update(coach_id, **kwargs)
