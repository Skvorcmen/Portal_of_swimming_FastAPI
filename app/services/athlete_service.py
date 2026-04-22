from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.repositories.athlete_profile_repository import AthleteProfileRepository
from app.repositories.personal_best_repository import PersonalBestRepository
from app.models import AthleteProfile, PersonalBest


class AthleteService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AthleteProfileRepository(session)
        self.pb_repo = PersonalBestRepository(session)

    async def create_athlete_profile(
        self,
        user_id: int,
        school_id: Optional[int] = None,
        coach_id: Optional[int] = None,
        birth_date: Optional[str] = None,
        gender: Optional[str] = None,
        rank: Optional[str] = None,
        photo_url: Optional[str] = None,
    ) -> AthleteProfile:
        return await self.repo.create(
            user_id=user_id,
            school_id=school_id,
            coach_id=coach_id,
            birth_date=birth_date,
            gender=gender,
            rank=rank,
            photo_url=photo_url,
        )

    async def get_athlete(self, athlete_id: int) -> Optional[AthleteProfile]:
        return await self.repo.get_by_id(athlete_id)

    async def get_athlete_with_details(self, athlete_id: int) -> Optional[AthleteProfile]:
        return await self.repo.get_by_id_with_details(athlete_id)

    async def get_athlete_by_user_id(self, user_id: int) -> Optional[AthleteProfile]:
        return await self.repo.get_by_user_id(user_id)

    async def get_athletes_by_school(self, school_id: int) -> List[AthleteProfile]:
        return await self.repo.get_by_school(school_id)

    async def update_athlete(self, athlete_id: int, **kwargs) -> Optional[AthleteProfile]:
        return await self.repo.update(athlete_id, **kwargs)

    async def delete_athlete(self, athlete_id: int) -> bool:
        return await self.repo.delete(athlete_id)

    async def add_personal_best(
        self,
        athlete_id: int,
        distance: int,
        stroke: str,
        time_seconds: float,
        set_date: str = None,
    ) -> PersonalBest:
        """Добавить личный рекорд"""
        from datetime import datetime
        data = {
            'athlete_id': athlete_id,
            'distance': distance,
            'stroke': stroke,
            'time_seconds': time_seconds,
        }
        if set_date:
            try:
                data['set_date'] = datetime.strptime(set_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        result = await self.pb_repo.create(**data)
        if hasattr(result, 'set_date') and result.set_date and not isinstance(result.set_date, str):
            result.set_date = result.set_date.isoformat()
        return result
    
    async def get_personal_bests(self, athlete_id: int) -> List[PersonalBest]:
        """Получить все личные рекорды спортсмена"""
        result = await self.pb_repo.get_by_athlete(athlete_id)
        for record in result:
            if hasattr(record, 'set_date') and record.set_date and not isinstance(record.set_date, str):
                record.set_date = record.set_date.isoformat()
        return result
    
    async def delete_personal_best(self, pb_id: int) -> bool:
        """Удалить личный рекорд"""
        return await self.pb_repo.delete(pb_id)

    async def get_personal_best(self, pb_id: int) -> Optional[PersonalBest]:
        """Получить личный рекорд по ID"""
        return await self.pb_repo.get_by_id(pb_id)
