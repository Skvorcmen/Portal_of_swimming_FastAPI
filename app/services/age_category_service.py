from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.repositories.age_category_repository import AgeCategoryRepository
from app.models import AgeCategory


class AgeCategoryService:
    """Сервис для работы с возрастными категориями"""

    def __init__(self, session: AsyncSession):
        self.repo = AgeCategoryRepository(session)

    async def create_age_category(
        self,
        competition_id: int,
        name: str,
        min_age: int,
        max_age: int,
        gender: Optional[str] = None,
    ) -> AgeCategory:
        """Создать возрастную категорию для соревнования"""
        return await self.repo.create(
            competition_id=competition_id,
            name=name,
            min_age=min_age,
            max_age=max_age,
            gender=gender,
        )

    async def get_age_category(self, category_id: int) -> Optional[AgeCategory]:
        """Получить возрастную категорию по ID"""
        return await self.repo.get_by_id(category_id)

    async def get_categories_by_competition(
        self, competition_id: int
    ) -> List[AgeCategory]:
        """Получить все категории для соревнования"""
        return await self.repo.get_by_competition(competition_id)

    async def update_age_category(
        self, category_id: int, **kwargs
    ) -> Optional[AgeCategory]:
        """Обновить возрастную категорию"""
        return await self.repo.update(category_id, **kwargs)

    async def delete_age_category(self, category_id: int) -> bool:
        """Удалить возрастную категорию"""
        return await self.repo.delete(category_id)
