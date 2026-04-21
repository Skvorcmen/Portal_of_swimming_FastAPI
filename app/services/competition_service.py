from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.repositories.competition_repository import CompetitionRepository
from app.models import Competition


class CompetitionService:
    """Сервис для работы с соревнованиями"""

    def __init__(self, session: AsyncSession):
        self.repo = CompetitionRepository(session)

    async def create_competition(
        self,
        name: str,
        start_date,
        end_date,
        created_by: int,
        description: Optional[str] = None,
        venue: Optional[str] = None,
        city: Optional[str] = None,
        status: str = "draft",
        max_participants: int = 0,
    ) -> Competition:
        """Создать новое соревнование"""
        competition = await self.repo.create(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            venue=venue,
            city=city,
            status=status,
            max_participants=max_participants,
            created_by=created_by,
        )
        return competition

    async def get_competition(self, competition_id: int) -> Optional[Competition]:
        """Получить соревнование по ID"""
        return await self.repo.get_by_id(competition_id)

    async def get_all_competitions(
        self, skip: int = 0, limit: int = 100
    ) -> List[Competition]:
        """Получить список всех соревнований"""
        return await self.repo.get_all(skip, limit)

    async def update_competition(
        self, competition_id: int, **kwargs
    ) -> Optional[Competition]:
        """Обновить соревнование"""
        return await self.repo.update(competition_id, **kwargs)

    async def delete_competition(self, competition_id: int) -> bool:
        """Удалить соревнование"""
        return await self.repo.delete(competition_id)

    async def get_active_competitions(self) -> List[Competition]:
        """Получить активные соревнования"""
        return await self.repo.get_active()

    async def get_upcoming_competitions(self) -> List[Competition]:
        """Получить предстоящие соревнования"""
        return await self.repo.get_upcoming()

    async def search_competitions(
        self, name: str = "", city: str = "", status: str = "", page: int = 1
    ) -> dict:
        return await self.repo.search(name, city, status, page)
