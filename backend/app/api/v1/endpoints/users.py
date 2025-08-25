from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_async_session
from app.api.v1.schemas.user import User, UserUpdate, UserPasswordUpdate, UserWithSubscription
from app.core.security import get_current_active_user, get_password_hash, verify_password
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserWithSubscription)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получение информации о текущем пользователе"""
    user_service = UserService(db)
    user = await user_service.get_with_subscription(current_user.id)
    return user


@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Обновление информации о текущем пользователе"""
    user_service = UserService(db)
    
    # Проверяем, не занят ли новый username/email другим пользователем
    if user_update.username and user_update.username != current_user.username:
        existing_user = await user_service.get_by_username(user_update.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username уже занят"
            )
    
    if user_update.email and user_update.email != current_user.email:
        existing_user = await user_service.get_by_email(user_update.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже занят"
            )
    
    # Обновляем пользователя
    updated_user = await user_service.update(
        current_user.id,
        **user_update.dict(exclude_unset=True)
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return updated_user


@router.put("/me/password")
async def change_password(
    password_update: UserPasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Изменение пароля текущего пользователя"""
    user_service = UserService(db)
    
    # Проверяем текущий пароль
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный текущий пароль"
        )
    
    # Обновляем пароль
    new_hashed_password = get_password_hash(password_update.new_password)
    await user_service.update(
        current_user.id,
        hashed_password=new_hashed_password
    )
    
    return {"message": "Пароль успешно изменен"}


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получение информации о пользователе по ID (только для собственного профиля)"""
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к профилю другого пользователя"
        )
    
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return user


@router.delete("/me")
async def delete_current_user(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Удаление аккаунта текущего пользователя"""
    user_service = UserService(db)
    
    success = await user_service.delete(current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return {"message": "Аккаунт успешно удален"}