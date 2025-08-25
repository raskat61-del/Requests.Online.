from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.project import Project
from app.models.keyword import Keyword
from app.models.search_task import SearchTask
from app.models.collected_data import CollectedData
from app.models.analysis import Cluster, TextAnalysis
from app.models.report import Report, UserSubscription
from app.api.v1.schemas.project import ProjectStats


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
    
    async def count_user_projects(self, user_id: int) -> int:
        """Подсчет количества проектов пользователя"""
        result = await self.db.execute(
            select(func.count(Project.id)).where(Project.user_id == user_id)
        )
        return result.scalar()
    
    async def get_user_subscription(self, user_id: int) -> Optional[UserSubscription]:
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
    
    async def get_project_stats(self, project_id: int) -> ProjectStats:
        """Получение статистики проекта"""
        # Подсчет ключевых слов
        keywords_result = await self.db.execute(
            select(func.count(Keyword.id))
            .where(Keyword.project_id == project_id)
        )
        keywords_count = keywords_result.scalar()
        
        # Подсчет задач поиска
        tasks_result = await self.db.execute(
            select(func.count(SearchTask.id))
            .where(SearchTask.project_id == project_id)
        )
        tasks_count = tasks_result.scalar()
        
        # Подсчет собранных данных
        data_result = await self.db.execute(
            select(func.count(CollectedData.id))
            .select_from(CollectedData)
            .join(SearchTask)
            .where(SearchTask.project_id == project_id)
        )
        collected_data_count = data_result.scalar()
        
        # Подсчет кластеров
        clusters_result = await self.db.execute(
            select(func.count(Cluster.id))
            .where(Cluster.project_id == project_id)
        )
        clusters_count = clusters_result.scalar()
        
        # Подсчет отчетов
        reports_result = await self.db.execute(
            select(func.count(Report.id))
            .where(Report.project_id == project_id)
        )
        reports_count = reports_result.scalar()
        
        # Средняя тональность
        sentiment_result = await self.db.execute(
            select(func.avg(TextAnalysis.sentiment_score))
            .select_from(TextAnalysis)
            .join(CollectedData)
            .join(SearchTask)
            .where(SearchTask.project_id == project_id)
        )
        avg_sentiment = sentiment_result.scalar()
        
        return ProjectStats(
            keywords_count=keywords_count,
            tasks_count=tasks_count,
            collected_data_count=collected_data_count,
            clusters_count=clusters_count,
            reports_count=reports_count,
            avg_sentiment=avg_sentiment
        )