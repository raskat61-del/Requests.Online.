# Импорт всех моделей для регистрации в SQLAlchemy

from .user import User
from .project import Project
from .keyword import Keyword, SearchSource
from .search_task import SearchTask
from .collected_data import CollectedData
from .analysis import TextAnalysis, Cluster, FrequencyAnalysis, ApiUsage
from .report import Report, UserSubscription

__all__ = [
    "User",
    "Project", 
    "Keyword",
    "SearchSource",
    "SearchTask",
    "CollectedData",
    "TextAnalysis",
    "Cluster",
    "FrequencyAnalysis",
    "ApiUsage",
    "Report",
    "UserSubscription"
]