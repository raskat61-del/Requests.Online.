from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Keyword(Base):
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    keyword = Column(String(500), nullable=False)
    category = Column(String(100))  # pain_points, solutions, complaints, etc.
    priority = Column(Integer, default=1)  # 1-5 приоритет
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Отношения
    project = relationship("Project", back_populates="keywords")
    search_tasks = relationship("SearchTask", back_populates="keyword", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Keyword(id={self.id}, keyword='{self.keyword}', project_id={self.project_id})>"


class SearchSource(Base):
    __tablename__ = "search_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)  # google, yandex, telegram, vk, reddit, forums
    is_enabled = Column(Boolean, default=True)
    api_config = Column(String)  # JSON конфигурация API
    rate_limit = Column(Integer, default=100)  # лимит запросов в час
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Отношения
    search_tasks = relationship("SearchTask", back_populates="source")
    api_usage = relationship("ApiUsage", back_populates="source")
    
    def __repr__(self):
        return f"<SearchSource(id={self.id}, name='{self.name}')>"