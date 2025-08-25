from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.report import UserSubscription


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
        
        # Создаем бесплатную подписку для нового пользователя
        subscription = UserSubscription(
            user_id=user.id,
            plan_name="free",
            max_projects=1,
            max_keywords_per_project=10,
            max_requests_per_day=100,
            price_per_month=0.00
        )
        self.db.add(subscription)
        await self.db.commit()
        
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
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
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
    
    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Получение списка пользователей"""
        result = await self.db.execute(
            select(User)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return result.scalars().all()
    
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
    
    async def delete(self, user_id: int) -> bool:
        """Удаление пользователя"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        await self.db.delete(user)
        await self.db.commit()
        return True
    
    async def get_with_subscription(self, user_id: int) -> Optional[User]:
        """Получение пользователя с подпиской"""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.subscriptions))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_subscription(self, user_id: int) -> Optional[UserSubscription]:
        """Получение активной подписки пользователя"""
        result = await self.db.execute(
            select(UserSubscription)
            .where(
                and_(
                    UserSubscription.user_id == user_id,
                    UserSubscription.is_active == True
                )
            )
            .order_by(UserSubscription.created_at.desc())
        )
        return result.scalar_one_or_none()
    
    async def count_users(self) -> int:
        """Подсчет общего количества пользователей"""
        result = await self.db.execute(
            select(func.count(User.id))
        )
        return result.scalar()
    
    async def count_active_users(self) -> int:
        """Подсчет активных пользователей"""
        result = await self.db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        return result.scalar()
    
    async def count_premium_users(self) -> int:
        """Подсчет премиум пользователей"""
        result = await self.db.execute(
            select(func.count(User.id)).where(User.is_premium == True)
        )
        return result.scalar()