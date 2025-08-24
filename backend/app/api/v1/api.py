from fastapi import APIRouter

from app.api.v1.endpoints import auth, projects, keywords, search, analysis, reports, users

api_router = APIRouter()

# Подключение всех роутов
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(keywords.router, prefix="/keywords", tags=["keywords"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])