from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from typing import AsyncGenerator

from app.core.config import settings


# Создание асинхронного движка БД
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Создание синхронного движка для миграций
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Фабрика сессий
async_session_maker = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Синхронная сессия для миграций
sync_session_maker = sessionmaker(
    sync_engine,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Зависимость для получения асинхронной сессии БД"""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Создание всех таблиц в БД"""
    # Импортируем все модели для их регистрации
    from app.models import user, project, keyword, search_task, collected_data, analysis, report
    
    async with async_engine.begin() as conn:
        # Создаем все таблицы
        await conn.run_sync(Base.metadata.create_all)