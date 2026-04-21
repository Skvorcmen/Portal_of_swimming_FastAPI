from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import List, Dict, Any
from app.repositories.entry_repository import EntryRepository
from app.repositories.heat_repository import HeatRepository, HeatEntryRepository
from app.models import Entry, Heat, HeatEntry, AthleteProfile, AgeCategory, SwimEvent


class HeatService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.heat_repo = HeatRepository(session)
        self.heat_entry_repo = HeatEntryRepository(session)

    async def generate_heats(self, swim_event_id: int) -> Dict[str, Any]:
        """Генерация заплывов для дистанции"""

        # 1. Получаем swim_event
        result = await self.session.execute(
            select(SwimEvent).where(SwimEvent.id == swim_event_id)
        )
        swim_event = result.scalar_one_or_none()
        if not swim_event:
            return {"message": "Swim event not found"}

        # 2. Получаем все заявки для дистанции с предварительной загрузкой связанных данных
        result = await self.session.execute(
            select(Entry)
            .where(Entry.swim_event_id == swim_event_id)
            .options(selectinload(Entry.athlete), selectinload(Entry.competition))
        )
        entries = result.scalars().all()

        if not entries:
            return {"message": "No entries for this swim event"}

        # 3. Получаем возрастные категории для соревнования
        competition_id = entries[0].competition_id
        result = await self.session.execute(
            select(AgeCategory).where(AgeCategory.competition_id == competition_id)
        )
        age_categories = result.scalars().all()

        # 4. Группируем по категориям
        groups = {}
        for entry in entries:
            athlete = entry.athlete
            if not athlete or not athlete.birth_date:
                continue

            # Расчёт возраста
            age = self._calculate_age(athlete.birth_date)

            # Поиск подходящей возрастной категории
            age_category = None
            for cat in age_categories:
                if cat.min_age <= age <= cat.max_age:
                    if cat.gender is None or cat.gender == athlete.gender:
                        age_category = cat
                        break

            if not age_category:
                continue

            # Ключ группы
            group_key = f"{age_category.id}_{athlete.gender or 'mixed'}_{swim_event.distance}_{swim_event.stroke}"

            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(entry)

        # 5. Для каждой группы создаём заплывы
        heats_created = []
        for group_key, group_entries in groups.items():
            # Сортируем по личному рекорду
            group_entries.sort(key=lambda e: e.entry_time or float("inf"))

            # Разбиваем на заплывы по 8 человек
            lane_count = 8
            for i in range(0, len(group_entries), lane_count):
                heat_entries = group_entries[i : i + lane_count]

                # Создаём заплыв
                heat = Heat(
                    swim_event_id=swim_event_id,
                    heat_number=len(heats_created) + 1,
                    lane_count=lane_count,
                    status="scheduled",
                )
                self.session.add(heat)
                await self.session.flush()

                # Расставляем по дорожкам (алгоритм FINA)
                lane_order = self._get_lane_order(len(heat_entries))

                for idx, entry in enumerate(heat_entries):
                    lane = lane_order[idx] if idx < len(lane_order) else None
                    if lane:
                        heat_entry = HeatEntry(
                            heat_id=heat.id, entry_id=entry.id, lane=lane
                        )
                        self.session.add(heat_entry)

                heats_created.append(heat)

        await self.session.commit()

        return {
            "message": f"Created {len(heats_created)} heats",
            "heats_count": len(heats_created),
        }

    def _calculate_age(self, birth_date) -> int:
        """Расчёт возраста"""
        from datetime import datetime, timezone

        today = datetime.now(timezone.utc)
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age

    def _get_lane_order(self, num_entries: int) -> List[int]:
        """Алгоритм FINA для расстановки по дорожкам"""
        center_lanes = [4, 5, 3, 6, 2, 7, 1, 8]
        return center_lanes[:num_entries]

    async def get_heats_by_swim_event(self, swim_event_id: int) -> List[Heat]:
        """Получить все заплывы для дистанции"""
        return await self.heat_repo.get_by_swim_event(swim_event_id)

    async def enter_result(self, heat_entry_id: int, result_time: float) -> HeatEntry:
        """Ввод результата для участника"""
        heat_entry = await self.heat_entry_repo.get_by_id(heat_entry_id)
        if not heat_entry:
            raise ValueError("Heat entry not found")

        # Обновляем результат
        heat_entry.result_time = result_time
        await self.heat_entry_repo.update(heat_entry_id, result_time=result_time)

        return heat_entry

    async def complete_heat(self, heat_id: int) -> Heat:
        """Завершить заплыв и рассчитать места"""
        heat = await self.heat_repo.get_by_id(heat_id)
        if not heat:
            raise ValueError("Heat not found")

        # Получаем все результаты заплыва
        entries = await self.heat_entry_repo.get_by_heat(heat_id)

        # Сортируем по времени (лучшее время - первое место)
        entries_sorted = sorted(
            [e for e in entries if e.result_time is not None],
            key=lambda e: e.result_time,
        )

        # Назначаем места
        for i, entry in enumerate(entries_sorted):
            entry.place = i + 1
            await self.heat_entry_repo.update(entry.id, place=entry.place)

        # Обновляем статус заплыва
        heat.status = "completed"
        heat.completed_at = datetime.now(timezone.utc)
        await self.heat_repo.update(
            heat_id, status="completed", completed_at=heat.completed_at
        )

        return heat

    async def get_heat_results(self, heat_id: int):
        """Получить результаты заплыва"""
        return await self.heat_entry_repo.get_by_heat(heat_id)

    async def get_live_results(self, competition_id: int) -> List[dict]:
        """Получить актуальные результаты для live-таблицы"""

        # Получаем все завершённые заплывы для соревнования
        from sqlalchemy.orm import selectinload

        result = await self.session.execute(
            select(Heat)
            .options(
                selectinload(Heat.entries)
                .selectinload(HeatEntry.entry)
                .selectinload(Entry.athlete)
                .selectinload(AthleteProfile.user)
            )
            .join(SwimEvent)
            .where(
                SwimEvent.competition_id == competition_id, Heat.status == "completed"
            )
        )
        heats = result.scalars().all()

        live_data = []
        for heat in heats:
            for heat_entry in heat.entries:
                athlete = heat_entry.entry.athlete
                user = athlete.user if athlete else None

                live_data.append(
                    {
                        "heat_number": heat.heat_number,
                        "lane": heat_entry.lane,
                        "athlete_name": (
                            user.full_name
                            if user
                            else f"Athlete {heat_entry.entry.athlete_id}"
                        ),
                        "result_time": heat_entry.result_time,
                        "place": heat_entry.place,
                    }
                )

        print(f"DEBUG: Found {len(live_data)} results")  # Временная отладка
        return live_data
