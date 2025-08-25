from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import uvicorn

from app.core.config import settings
from app.db.database import create_tables
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    # Создаем таблицы БД при запуске
    await create_tables()
    
    # Создаем необходимые директории
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    yield
    
    # Shutdown
    print("Shutting down...")


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API для бота-аналитика, который собирает и анализирует данные из различных источников",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan
    )
    
    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Middleware для доверенных хостов
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["*"]  # Разрешаем все хосты для development
    )
    
    # Подключение статических файлов
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Подключение API роутов
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    @app.get("/")
    async def root():
        return {
            "message": f"Добро пожаловать в {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "redoc": "/redoc"
        }
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": settings.APP_NAME}
    
    return app


# Создаем экземпляр приложения
app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )