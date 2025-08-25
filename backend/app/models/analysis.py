from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class TextAnalysis(Base):
    __tablename__ = "text_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    data_id = Column(Integer, ForeignKey("collected_data.id", ondelete="CASCADE"), nullable=False)
    sentiment_score = Column(Float)  # -1 to 1 (negative to positive)
    sentiment_label = Column(String(20))  # negative, neutral, positive
    keywords_extracted = Column(JSON)  # массив извлеченных ключевых слов
    topics = Column(JSON)  # массив топиков
    cluster_id = Column(Integer, ForeignKey("clusters.id"))  # ID кластера
    pain_points = Column(JSON)  # выявленные болевые точки
    confidence_score = Column(Float)  # уверенность анализа
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Отношения
    data = relationship("CollectedData", back_populates="text_analysis")
    cluster = relationship("Cluster", back_populates="text_analyses")
    
    def __repr__(self):
        return f"<TextAnalysis(id={self.id}, sentiment_label='{self.sentiment_label}', data_id={self.data_id})>"


class Cluster(Base):
    __tablename__ = "clusters"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200))
    description = Column(String)
    keywords = Column(JSON)  # основные ключевые слова кластера
    size = Column(Integer, default=0)  # количество документов в кластере
    avg_sentiment = Column(Float)  # средняя тональность
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Отношения
    project = relationship("Project", back_populates="clusters")
    text_analyses = relationship("TextAnalysis", back_populates="cluster")
    
    def __repr__(self):
        return f"<Cluster(id={self.id}, name='{self.name}', project_id={self.project_id})>"


class FrequencyAnalysis(Base):
    __tablename__ = "frequency_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    term = Column(String(200), nullable=False)
    frequency = Column(Integer, nullable=False)
    tf_idf_score = Column(Float)
    document_count = Column(Integer)  # в скольких документах встречается
    category = Column(String(100))  # pain_point, solution, complaint, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Отношения
    project = relationship("Project", back_populates="frequency_analysis")
    
    def __repr__(self):
        return f"<FrequencyAnalysis(id={self.id}, term='{self.term}', frequency={self.frequency})>"


class ApiUsage(Base):
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(Integer, ForeignKey("search_sources.id"), nullable=False)
    requests_count = Column(Integer, default=1)
    date = Column(DateTime(timezone=True), server_default=func.current_date())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Отношения
    user = relationship("User", back_populates="api_usage")
    source = relationship("SearchSource", back_populates="api_usage")
    
    def __repr__(self):
        return f"<ApiUsage(user_id={self.user_id}, source_id={self.source_id}, requests={self.requests_count})>"