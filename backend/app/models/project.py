from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="active")  # active, paused, completed, archived
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Отношения
    user = relationship("User", back_populates="projects")
    keywords = relationship("Keyword", back_populates="project", cascade="all, delete-orphan")
    search_tasks = relationship("SearchTask", back_populates="project", cascade="all, delete-orphan")
    clusters = relationship("Cluster", back_populates="project", cascade="all, delete-orphan")
    frequency_analysis = relationship("FrequencyAnalysis", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', user_id={self.user_id})>"