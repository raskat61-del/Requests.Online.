from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Numeric
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
    parameters = Column(Text)  # JSON параметры генерации отчета
    status = Column(String(20), default="generating")  # generating, completed, failed
    generated_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Отношения
    project = relationship("Project", back_populates="reports")
    
    def __repr__(self):
        return f"<Report(id={self.id}, name='{self.name}', type='{self.report_type}')>"


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_name = Column(String(50), nullable=False)  # free, basic, premium
    max_projects = Column(Integer, default=1)
    max_keywords_per_project = Column(Integer, default=10)
    max_requests_per_day = Column(Integer, default=100)
    price_per_month = Column(Numeric(10, 2))
    starts_at = Column(DateTime(timezone=True), server_default=func.now())
    ends_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Отношения
    user = relationship("User", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<UserSubscription(id={self.id}, user_id={self.user_id}, plan='{self.plan_name}')>"