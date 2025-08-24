from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
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