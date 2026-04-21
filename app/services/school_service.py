from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.repositories.school_repository import SchoolRepository
from app.models import School


class SchoolService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SchoolRepository(session)

    async def create_school(
        self,
        name: str,
        city: str,
        address: str,
        description: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        website: Optional[str] = None,
        logo_url: Optional[str] = None,
        cover_url: Optional[str] = None,
        founded_year: Optional[int] = None,
    ) -> School:
        return await self.repo.create(
            name=name,
            city=city,
            address=address,
            description=description,
            phone=phone,
            email=email,
            website=website,
            logo_url=logo_url,
            cover_url=cover_url,
            founded_year=founded_year,
        )

    async def get_school(self, school_id: int) -> Optional[School]:
        result = await self.session.execute(
            select(School).where(School.id == school_id)
        )
        return result.scalar_one_or_none()

    async def get_all_schools(self, skip: int = 0, limit: int = 100) -> List[School]:
        result = await self.session.execute(
            select(School).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def search_schools(self, name: str = "", city: str = "", page: int = 1) -> dict:
        return await self.repo.search(name, city, page)

    async def update_school(self, school_id: int, **kwargs) -> Optional[School]:
        return await self.repo.update(school_id, **kwargs)

    async def delete_school(self, school_id: int) -> bool:
        return await self.repo.delete(school_id)
