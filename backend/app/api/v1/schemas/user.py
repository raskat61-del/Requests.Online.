from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Базовые схемы для пользователя
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_premium: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class User(UserInDB):
    pass


# Схемы для аутентификации
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


# Схемы для подписок
class SubscriptionBase(BaseModel):
    plan_name: str
    max_projects: int
    max_keywords_per_project: int
    max_requests_per_day: int
    price_per_month: float


class SubscriptionCreate(SubscriptionBase):
    user_id: int
    ends_at: Optional[datetime] = None


class Subscription(SubscriptionBase):
    id: int
    user_id: int
    starts_at: datetime
    ends_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserWithSubscription(User):
    subscriptions: List[Subscription] = []