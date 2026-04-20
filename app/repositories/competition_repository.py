from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional, List
from app.models import Competition
from app.repositories.base import BaseRepository


class CompetitionRepository(BaseRepository[Competition]):
    """Репозиторий для работы с соревнованиями"""

    def __init__(self, session: AsyncSession):
        super().__init__(Competition, session)

    async def get_by_status(
        self, status: str, skip: int = 0, limit: int = 100
    ) -> List[Competition]:
        """Найти соревнования по статусу"""
        result = await self.session.execute(
            select(Competition)
            .where(Competition.status == status)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_active(self, skip: int = 0, limit: int = 100) -> List[Competition]:
        result = await self.session.execute(
            select(Competition)
            .where(
                Competition.status.in_(
                    [
                        "registration_open",
                        "registration_closed",
                        "ongoing",
                    ]
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_upcoming(self, skip: int = 0, limit: int = 100) -> List[Competition]:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            select(Competition)
            .where(Competition.start_date > now)
            .where(Competition.status != "cancelled")
            .order_by(Competition.start_date)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_upcoming(self, skip: int = 0, limit: int = 100) -> List[Competition]:
        """Найти предстоящие соревнования"""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            select(Competition)
            .where(Competition.start_date > now)
            .where(Competition.status != "cancelled")
            .order_by(Competition.start_date)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
