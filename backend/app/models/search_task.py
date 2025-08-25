from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class SearchTask(Base):
    __tablename__ = "search_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    keyword_id = Column(Integer, ForeignKey("keywords.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(Integer, ForeignKey("search_sources.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    scheduled_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    results_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Отношения
    project = relationship("Project", back_populates="search_tasks")
    keyword = relationship("Keyword", back_populates="search_tasks")
    source = relationship("SearchSource", back_populates="search_tasks")
    collected_data = relationship("CollectedData", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SearchTask(id={self.id}, status='{self.status}', project_id={self.project_id})>"
