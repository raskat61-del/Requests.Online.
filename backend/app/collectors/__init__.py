"""
Модуль коллекторов данных для Analytics Bot

Этот модуль содержит различные коллекторы для сбора данных из различных источников:
- Google Search API
- Yandex Search API  
- Telegram каналы и группы
- VKontakte (планируется)
- Reddit (планируется)
- Веб-форумы (планируется)
"""

from .base import BaseCollector, SearchResult
from .google_search import GoogleSearchCollector
from .yandex_search import YandexSearchCollector
from .telegram import TelegramCollector
from .vkontakte import VKontakteCollector
from .reddit import RedditCollector
from .web_scraper import WebScraperCollector
from .manager import CollectorManager, CollectorConfig

__all__ = [
    "BaseCollector",
    "SearchResult", 
    "GoogleSearchCollector",
    "YandexSearchCollector",
    "TelegramCollector",
    "VKontakteCollector",
    "RedditCollector",
    "WebScraperCollector",
    "CollectorManager",
    "CollectorConfig"
]