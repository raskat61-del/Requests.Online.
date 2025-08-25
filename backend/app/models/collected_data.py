from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class CollectedData(Base):
    __tablename__ = "collected_data"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("search_tasks.id", ondelete="CASCADE"), nullable=False)
    source_type = Column(String(50), nullable=False)  # google, yandex, telegram, etc.
    source_url = Column(Text)
    title = Column(Text)
    content = Column(Text, nullable=False)
    author = Column(String(200))
    published_at = Column(DateTime(timezone=True))
    metadata_info = Column(JSON)  # дополнительные данные (лайки, репосты, etc.)
    language = Column(String(10), default="ru")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Отношения
    task = relationship("SearchTask", back_populates="collected_data")
    text_analysis = relationship("TextAnalysis", back_populates="data", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CollectedData(id={self.id}, source_type='{self.source_type}', task_id={self.task_id})>"