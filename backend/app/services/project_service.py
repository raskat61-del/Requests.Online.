from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.project import Project


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        user_id: int,
        name: str,
        description: Optional[str] = None,
        status: str = "active"
    ) -> Project:
        """Создание нового проекта"""
        project = Project(
            user_id=user_id,
            name=name,
            description=description,
            status=status
        )
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project
    
    async def get_by_id(self, project_id: int) -> Optional[Project]:
        """Получение проекта по ID"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_projects(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Project]:
        """Получение проектов пользователя"""
        query = select(Project).where(Project.user_id == user_id)
        
        if status:
            query = query.where(Project.status == status)
        
        query = query.offset(skip).limit(limit).order_by(Project.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update(
        self,
        project_id: int,
        **kwargs
    ) -> Optional[Project]:
        """Обновление проекта"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            return None
        
        for field, value in kwargs.items():
            if hasattr(project, field) and value is not None:
                setattr(project, field, value)
        
        await self.db.commit()
        await self.db.refresh(project)
        return project
    
    async def delete(self, project_id: int) -> bool:
        """Удаление проекта"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            return False
        
        await self.db.delete(project)
        await self.db.commit()
        return True