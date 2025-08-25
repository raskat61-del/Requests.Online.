from pydantic_settings import BaseSettings
from typing import Optional
import os
from functools import lru_cache


class Settings(BaseSettings):
    # Основные настройки приложения
    APP_NAME: str = "Analytics Bot API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    # Безопасность
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 дней
    
    # База данных
    DATABASE_URL: str = "postgresql://analytics_user:password@localhost:5432/analytics_db"
    ASYNC_DATABASE_URL: str = "postgresql+asyncpg://analytics_user:password@localhost:5432/analytics_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # API ключи для поисковых систем
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_SEARCH_ENGINE_ID: Optional[str] = None
    YANDEX_API_KEY: Optional[str] = None
    
    # API ключи для социальных сетей
    TELEGRAM_API_ID: Optional[str] = None
    TELEGRAM_API_HASH: Optional[str] = None
    VK_ACCESS_TOKEN: Optional[str] = None
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USER_AGENT: str = "AnalyticsBot:v1.0.0 (by /u/yourusername)"
    
    # Настройки файлов и хранилища
    UPLOAD_DIR: str = "uploads"
    REPORTS_DIR: str = "reports"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # CORS настройки
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080"
    ]
    
    # Настройки парсинга
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    REQUEST_DELAY: float = 1.0  # Задержка между запросами в секундах
    MAX_RETRIES: int = 3
    TIMEOUT: int = 30
    
    # Лимиты для пользователей
    FREE_TIER_MAX_PROJECTS: int = 1
    FREE_TIER_MAX_KEYWORDS: int = 10
    FREE_TIER_MAX_REQUESTS_PER_DAY: int = 100
    
    BASIC_TIER_MAX_PROJECTS: int = 5
    BASIC_TIER_MAX_KEYWORDS: int = 50
    BASIC_TIER_MAX_REQUESTS_PER_DAY: int = 500
    
    PREMIUM_TIER_MAX_PROJECTS: int = 20
    PREMIUM_TIER_MAX_KEYWORDS: int = 200
    PREMIUM_TIER_MAX_REQUESTS_PER_DAY: int = 2000
    
    # Email настройки (для уведомлений)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Логирование
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Мониторинг
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 8001
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Экземпляр настроек для импорта
settings = get_settings()