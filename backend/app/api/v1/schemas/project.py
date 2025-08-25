from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ProjectStatus(str, Enum):
    active = "active"
    paused = "paused"
    completed = "completed"
    archived = "archived"


# Базовые схемы для проекта
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.active


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ProjectInDB(ProjectBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Project(ProjectInDB):
    pass


# Статистика проекта
class ProjectStats(BaseModel):
    keywords_count: int = 0
    tasks_count: int = 0
    collected_data_count: int = 0
    clusters_count: int = 0
    reports_count: int = 0
    avg_sentiment: Optional[float] = None


class ProjectWithStats(Project):
    stats: ProjectStats