import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings
from app.models import Base

async def init_db():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Создаём все таблицы
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Все таблицы созданы")
        
        # Проверяем созданные таблицы
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = result.fetchall()
        print(f"📊 Создано таблиц: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
