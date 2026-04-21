from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, desc
from typing import Optional, List
from app.models import School
from app.repositories.base import BaseRepository


class SchoolRepository(BaseRepository[School]):
    def __init__(self, session: AsyncSession):
        super().__init__(School, session)

    async def get_by_city(self, city: str) -> List[School]:
        result = await self.session.execute(select(School).where(School.city == city))
        return result.scalars().all()

    async def search(
        self, name: str = "", city: str = "", page: int = 1, limit: int = 10
    ) -> dict:
        stmt = select(School)
        filters = []

        if name:
            filters.append(School.name.ilike(f"%{name}%"))
        if city:
            filters.append(School.city.ilike(f"%{city}%"))

        if filters:
            stmt = stmt.where(or_(*filters))

        stmt = stmt.order_by(School.name)

        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        result = await self.session.execute(stmt)
        items = result.scalars().all()

        count_stmt = select(func.count()).select_from(School)
        if filters:
            count_stmt = count_stmt.where(or_(*filters))
        total = await self.session.scalar(count_stmt)

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total else 1,
        }
