from sqlalchemy import select
from datetime import datetime, timezone
from app.core.logging_config import logger

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

    async def send_results_notifications(self, competition_id: int) -> None:
        """Отправить уведомления подписчикам о завершении соревнования"""
        from app.models import CompetitionSubscription, User
        from app.core.email import send_email
        
        # Получаем соревнование
        competition = await self.get_competition(competition_id)
        if not competition:
            return
        
        # Получаем всех подписчиков
        result = await self.session.execute(
            select(CompetitionSubscription).where(
                CompetitionSubscription.competition_id == competition_id
            )
        )
        subscribers = result.scalars().all()
        
        if not subscribers:
            return
        
        # Получаем email подписчиков
        user_ids = [sub.user_id for sub in subscribers]
        users_result = await self.session.execute(
            select(User).where(User.id.in_(user_ids))
        )
        users = users_result.scalars().all()
        
        # Создаем новость на портале
        from app.models import News
        news = News(
            title=f"Завершены соревнования: {competition.name}",
            content=f"Соревнования {competition.name} завершены. Результаты доступны на странице соревнования.",
            is_published=True,
            published_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(news)
        
        # Отправляем email каждому подписчику
        results_link = f"http://localhost:8000/competitions/{competition_id}/page"
        
        for user in users:
            if user.email:
                await send_email(
                    to_email=user.email,
                    subject=f"Результаты соревнования: {competition.name}",
                    template_name="competition_results.html",
                    context={
                        "user_name": user.full_name,
                        "competition_name": competition.name,
                        "results_link": results_link,
                        "competition": competition
                    }
                )
        
        await self.session.commit()
        logger.info(f"Sent results notifications for competition {competition_id} to {len(users)} subscribers")
