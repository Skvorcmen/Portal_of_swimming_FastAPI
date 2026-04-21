from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app.models import AthleteProfile, CoachProfile
from app.repositories.base import BaseRepository


class AthleteProfileRepository(BaseRepository[AthleteProfile]):
    def __init__(self, session: AsyncSession):
        super().__init__(AthleteProfile, session)

    async def get_by_school(self, school_id: int) -> List[AthleteProfile]:
        result = await self.session.execute(
            select(AthleteProfile).where(AthleteProfile.school_id == school_id)
        )
        return result.scalars().all()

    async def get_by_coach(self, coach_id: int) -> List[AthleteProfile]:
        result = await self.session.execute(
            select(AthleteProfile).where(AthleteProfile.coach_id == coach_id)
        )
        return result.scalars().all()

    async def get_by_user_id(self, user_id: int) -> Optional[AthleteProfile]:
        result = await self.session.execute(
            select(AthleteProfile).where(AthleteProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_details(self, athlete_id: int) -> Optional[AthleteProfile]:
        result = await self.session.execute(
            select(AthleteProfile)
            .options(
                selectinload(AthleteProfile.user),
                selectinload(AthleteProfile.school),
                selectinload(AthleteProfile.coach).selectinload(CoachProfile.user),
                selectinload(AthleteProfile.personal_bests)
            )
            .where(AthleteProfile.id == athlete_id)
        )
        return result.scalar_one_or_none()
