from sqlalchemy.ext.asyncio import AsyncSession
from app.models import PersonalBest
from app.repositories.base import BaseRepository


class PersonalBestRepository(BaseRepository[PersonalBest]):
    def __init__(self, session: AsyncSession):
        super().__init__(PersonalBest, session)
