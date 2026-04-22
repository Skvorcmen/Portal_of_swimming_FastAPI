import csv
from io import StringIO, BytesIO
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime


class CSVService:
    
    @staticmethod
    async def export_competition_results(competition_id: int, db: AsyncSession) -> BytesIO:
        """Экспорт результатов соревнования в CSV"""
        
        # Получаем данные
        result = await db.execute(
            text("""
                SELECT 
                    c.name as competition_name,
                    se.name as event_name,
                    se.distance,
                    se.stroke,
                    a.gender,
                    u.full_name as athlete_name,
                    s.name as school_name,
                    he.result_time,
                    he.place,
                    h.heat_number,
                    he.lane
                FROM competitions c
                JOIN swim_events se ON se.competition_id = c.id
                JOIN entries e ON e.swim_event_id = se.id
                JOIN heat_entries he ON he.entry_id = e.id
                JOIN athlete_profiles a ON a.id = e.athlete_id
                JOIN "user" u ON u.id = a.user_id
                LEFT JOIN schools s ON s.id = a.school_id
                JOIN heats h ON h.id = he.heat_id
                WHERE c.id = :competition_id AND he.result_time IS NOT NULL
                ORDER BY se.order, he.place
            """),
            {"competition_id": competition_id}
        )
        
        rows = result.fetchall()
        
        # Создаем CSV в памяти
        output = StringIO()
        writer = csv.writer(output, delimiter=';')
        
        # Заголовки
        writer.writerow([
            'Соревнование', 'Дистанция', 'Стиль', 'Пол',
            'Спортсмен', 'Школа', 'Результат (сек)', 'Место',
            'Заплыв', 'Дорожка', 'Дата экспорта'
        ])
        
        # Данные
        for row in rows:
            writer.writerow([
                row.competition_name,
                f"{row.distance}м",
                row.stroke,
                row.gender or 'mixed',
                row.athlete_name,
                row.school_name or '-',
                row.result_time,
                row.place or '-',
                row.heat_number,
                row.lane,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Конвертируем в BytesIO для отправки
        output_bytes = BytesIO()
        output_bytes.write(output.getvalue().encode('utf-8-sig'))
        output_bytes.seek(0)
        
        return output_bytes
    
    @staticmethod
    async def export_athlete_results(athlete_id: int, db: AsyncSession) -> BytesIO:
        """Экспорт результатов конкретного спортсмена"""
        
        result = await db.execute(
            text("""
                SELECT 
                    c.name as competition_name,
                    c.start_date,
                    se.name as event_name,
                    se.distance,
                    se.stroke,
                    he.result_time,
                    he.place
                FROM athlete_profiles a
                JOIN entries e ON e.athlete_id = a.id
                JOIN swim_events se ON se.id = e.swim_event_id
                JOIN competitions c ON c.id = se.competition_id
                JOIN heat_entries he ON he.entry_id = e.id
                WHERE a.id = :athlete_id AND he.result_time IS NOT NULL
                ORDER BY c.start_date DESC
            """),
            {"athlete_id": athlete_id}
        )
        
        rows = result.fetchall()
        
        output = StringIO()
        writer = csv.writer(output, delimiter=';')
        
        writer.writerow([
            'Соревнование', 'Дата', 'Дистанция', 'Стиль', 
            'Результат (сек)', 'Место'
        ])
        
        for row in rows:
            writer.writerow([
                row.competition_name,
                row.start_date.strftime('%d.%m.%Y') if row.start_date else '-',
                f"{row.distance}м",
                row.stroke,
                row.result_time,
                row.place or '-'
            ])
        
        output_bytes = BytesIO()
        output_bytes.write(output.getvalue().encode('utf-8-sig'))
        output_bytes.seek(0)
        
        return output_bytes
