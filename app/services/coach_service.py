from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
from app.repositories.coach_repository import CoachRepository
from app.models import CoachProfile


class CoachService:
    def __init__(self, session: AsyncSession):
        self.repo = CoachRepository(session)

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
