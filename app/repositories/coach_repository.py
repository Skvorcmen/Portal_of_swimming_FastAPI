from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app.models import CoachProfile, User
from app.repositories.base import BaseRepository


class CoachRepository(BaseRepository[CoachProfile]):
    def __init__(self, session: AsyncSession):
        super().__init__(CoachProfile, session)

    async def get_by_school(self, school_id: int) -> List[CoachProfile]:
        result = await self.session.execute(
            select(CoachProfile)
            .options(selectinload(CoachProfile.user))
            .where(CoachProfile.school_id == school_id)
        )
        return result.scalars().all()

    async def get_by_id(self, coach_id: int) -> Optional[CoachProfile]:
        result = await self.session.execute(
            select(CoachProfile)
            .options(selectinload(CoachProfile.user))
            .where(CoachProfile.id == coach_id)
        )
        return result.scalar_one_or_none()

    async def search(self, name: str = "", school_id: int = None) -> List[CoachProfile]:
        stmt = select(CoachProfile).options(selectinload(CoachProfile.user))
        
        if name:
            stmt = stmt.join(User).where(User.full_name.ilike(f"%{name}%"))
        if school_id:
            stmt = stmt.where(CoachProfile.school_id == school_id)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
