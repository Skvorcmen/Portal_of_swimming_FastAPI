from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.repositories.swim_event_repository import SwimEventRepository
from app.models import SwimEvent


class SwimEventService:
    def __init__(self, session: AsyncSession):
        self.repo = SwimEventRepository(session)

    async def create_swim_event(
        self,
        competition_id: int,
        name: str,
        distance: int,
        stroke: str,
        gender: Optional[str] = None,
        is_relay: bool = False,
        order: int = 0,
    ) -> SwimEvent:
        return await self.repo.create(
            competition_id=competition_id,
            name=name,
            distance=distance,
            stroke=stroke,
            gender=gender,
            is_relay=is_relay,
            order=order,
        )

    async def get_by_competition(self, competition_id: int) -> List[SwimEvent]:
        return await self.repo.get_by_competition(competition_id)

    async def get_swim_event(self, event_id: int) -> Optional[SwimEvent]:
        return await self.repo.get_by_id(event_id)

    async def update_swim_event(self, event_id: int, **kwargs) -> Optional[SwimEvent]:
        return await self.repo.update(event_id, **kwargs)

    async def delete_swim_event(self, event_id: int) -> bool:
        return await self.repo.delete(event_id)
