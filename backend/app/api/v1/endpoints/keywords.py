from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_async_session
from app.api.v1.schemas.user import User
from app.core.security import get_current_active_user

router = APIRouter()


@router.get("/")
async def get_keywords(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получение списка ключевых слов"""
    # TODO: Реализовать получение ключевых слов
    return {"message": "Эндпоинт в разработке"}


@router.post("/")
async def create_keyword(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Создание нового ключевого слова"""
    # TODO: Реализовать создание ключевого слова
    return {"message": "Эндпоинт в разработке"}