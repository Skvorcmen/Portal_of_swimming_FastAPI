import asyncio
from sqlalchemy import text
from app.database import engine, Base
from app.models import *
from app.core.logging_config import logger

async def init_production_db():
    """Инициализация production базы данных"""
    try:
        async with engine.begin() as conn:
            # Создаем все таблицы
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Все таблицы успешно созданы")
            
            # Проверяем созданные таблицы
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.fetchall()
            logger.info(f"📊 Создано таблиц: {len(tables)}")
            for table in tables:
                logger.info(f"   - {table[0]}")
            
            # Создаем индексы по одному (asyncpg не поддерживает несколько команд)
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_chat_messages_room_created ON chat_messages(room, created_at DESC);",
                "CREATE INDEX IF NOT EXISTS idx_entries_competition_status ON entries(competition_id, status);",
                "CREATE INDEX IF NOT EXISTS idx_heat_entries_heat_lane ON heat_entries(heat_id, lane);",
                "CREATE INDEX IF NOT EXISTS idx_swim_events_competition ON swim_events(competition_id);",
                "CREATE INDEX IF NOT EXISTS idx_age_categories_competition ON age_categories(competition_id);",
            ]
            
            for index_sql in indexes:
                try:
                    await conn.execute(text(index_sql))
                    logger.info(f"   ✅ Индекс создан")
                except Exception as e:
                    logger.warning(f"   ⚠️ Индекс уже существует или ошибка: {e}")
            
            await conn.commit()
            logger.info("✅ Все индексы созданы")
            
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_production_db())
