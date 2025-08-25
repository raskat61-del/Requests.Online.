from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.db.database import get_async_session
from app.api.v1.schemas.user import UserCreate, User, Token, UserLogin
from app.core.config import settings
from app.core.security import (
    create_access_token, 
    create_refresh_token, 
    verify_password, 
    get_password_hash,
    decode_token
)
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """Регистрация нового пользователя"""
    user_service = UserService(db)
    
    # Если username не предоставлен, генерируем его из email
    username = user_data.username
    if not username:
        # Извлекаем часть до @ и очищаем от спецсимволов
        email_prefix = user_data.email.split('@')[0]
        username = ''.join(c for c in email_prefix if c.isalnum() or c in '_-')
        
        # Проверяем уникальность и добавляем суффикс если нужно
        base_username = username
        counter = 1
        while await user_service.get_by_username(username):
            username = f"{base_username}{counter}"
            counter += 1
    
    # Проверяем, не существует ли пользователь с таким username или email
    existing_user = await user_service.get_by_username_or_email(
        username, 
        user_data.email
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким username или email уже существует"
        )
    
    # Хешируем пароль
    hashed_password = get_password_hash(user_data.password)
    
    # Создаем пользователя
    user = await user_service.create(
        username=username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    
    return user


@router.post("/login", response_model=Token)
async def auth_login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_async_session)
):
    """Авторизация пользователя через email"""
    user_service = UserService(db)
    
    # Ищем пользователя по email
    user = await user_service.get_by_email(user_data.email)
    if not user:
        # Если не найден по email, ищем по username
        user = await user_service.get_by_username(user_data.email)
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Аккаунт деактивирован"
        )
    
    # Создаем токены
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username}, 
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/oauth2/login", response_model=Token)
async def oauth2_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session)
):
    """Авторизация пользователя"""
    user_service = UserService(db)
    
    # Ищем пользователя сначала по username, потом по email
    user = await user_service.get_by_username(form_data.username)
    if not user:
        # Если не найден по username, ищем по email
        user = await user_service.get_by_email(form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный username/email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Аккаунт деактивирован"
        )
    
    # Создаем токены
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username}, 
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/login-json", response_model=Token)
async def login_json(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_async_session)
):
    """Авторизация пользователя через JSON"""
    user_service = UserService(db)
    
    # Ищем пользователя сначала по email, потом по username
    user = await user_service.get_by_email(user_data.email)
    if not user:
        # Если не найден по email, ищем по username
        user = await user_service.get_by_username(user_data.email)
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email/username или пароль",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Аккаунт деактивирован"
        )
    
    # Создаем токены
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username}, 
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_async_session)
):
    """Обновление access токена"""
    try:
        payload = decode_token(refresh_token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалидный refresh токен",
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный refresh токен",
        )
    
    user_service = UserService(db)
    user = await user_service.get_by_username(username)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или деактивирован",
        )
    
    # Создаем новые токены
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": user.username}, 
        expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(
        data={"sub": user.username}, 
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }