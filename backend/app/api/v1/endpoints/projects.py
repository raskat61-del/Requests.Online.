from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_async_session
from app.api.v1.schemas.project import Project, ProjectCreate, ProjectUpdate, ProjectWithStats
from app.api.v1.schemas.user import User
from app.core.security import get_current_active_user
from app.services.project_service import ProjectService

router = APIRouter()


@router.get("/", response_model=List[ProjectWithStats])
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: str = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получение списка проектов пользователя"""
    project_service = ProjectService(db)
    projects = await project_service.get_user_projects(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )
    return projects


@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Создание нового проекта"""
    project_service = ProjectService(db)
    
    # Проверяем лимиты пользователя
    user_projects_count = await project_service.count_user_projects(current_user.id)
    user_subscription = await project_service.get_user_subscription(current_user.id)
    
    if user_subscription and user_projects_count >= user_subscription.max_projects:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Достигнут лимит проектов ({user_subscription.max_projects})"
        )
    
    project = await project_service.create(
        user_id=current_user.id,
        name=project_data.name,
        description=project_data.description,
        status=project_data.status
    )
    
    return project


@router.get("/{project_id}", response_model=ProjectWithStats)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получение проекта по ID"""
    project_service = ProjectService(db)
    project = await project_service.get_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )
    
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому проекту"
        )
    
    # Добавляем статистику
    stats = await project_service.get_project_stats(project_id)
    project_with_stats = ProjectWithStats(**project.__dict__, stats=stats)
    
    return project_with_stats


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Обновление проекта"""
    project_service = ProjectService(db)
    project = await project_service.get_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )
    
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому проекту"
        )
    
    updated_project = await project_service.update(
        project_id,
        **project_update.dict(exclude_unset=True)
    )
    
    return updated_project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Удаление проекта"""
    project_service = ProjectService(db)
    project = await project_service.get_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )
    
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому проекту"
        )
    
    success = await project_service.delete(project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении проекта"
        )
    
    return {"message": "Проект успешно удален"}