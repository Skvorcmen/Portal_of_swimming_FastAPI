from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional, List
from app.models import Competition
from app.repositories.base import BaseRepository
from sqlalchemy import select, desc, func, and_


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

    async def search(
        self,
        name: str = "",
        city: str = "",
        status: str = "",
        page: int = 1,
        limit: int = 10,
    ) -> dict:
        from sqlalchemy import func, and_, desc

        stmt = select(Competition)
        filters = []
        if name:
            filters.append(Competition.name.ilike(f"%{name}%"))
        if city:
            filters.append(Competition.city.ilike(f"%{city}%"))
        if status:
            filters.append(Competition.status == status)

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.order_by(desc(Competition.start_date))

        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        items = result.scalars().all()

        count_stmt = select(func.count()).select_from(Competition)
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        total = await self.session.scalar(count_stmt)

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total else 1,
        }
