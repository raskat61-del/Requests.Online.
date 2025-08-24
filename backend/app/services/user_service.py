from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func

from app.models.user import User


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        username: str,
        email: str,
        hashed_password: str,
        full_name: Optional[str] = None
    ) -> User:
        """Создание нового пользователя"""
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по username"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username_or_email(
        self, username: str, email: str
    ) -> Optional[User]:
        """Получение пользователя по username или email"""
        result = await self.db.execute(
            select(User).where(
                or_(User.username == username, User.email == email)
            )
        )
        return result.scalar_one_or_none()
    
    async def update(
        self,
        user_id: int,
        **kwargs
    ) -> Optional[User]:
        """Обновление пользователя"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        for field, value in kwargs.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user