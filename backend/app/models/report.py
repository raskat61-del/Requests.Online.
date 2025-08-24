from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False)  # summary, detailed, sentiment, clusters
    format = Column(String(10), nullable=False)  # pdf, excel, json
    file_path = Column(String(500))
    file_size = Column(Integer)
    parameters = Column(JSON)  # параметры генерации отчета
    status = Column(String(20), default="generating")  # generating, completed, failed
    generated_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Отношения
    project = relationship("Project", back_populates="reports")
    
    def __repr__(self):
        return f"<Report(id={self.id}, name='{self.name}', project_id={self.project_id})>"