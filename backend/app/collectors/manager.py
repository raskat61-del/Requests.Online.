from typing import List, Dict, Any, Optional, Type
from dataclasses import dataclass
import asyncio
from loguru import logger

from app.collectors.base import BaseCollector, SearchResult
from app.collectors.google_search import GoogleSearchCollector
from app.collectors.yandex_search import YandexSearchCollector
from app.collectors.telegram import TelegramCollector
from app.collectors.vkontakte import VKontakteCollector
from app.collectors.reddit import RedditCollector
from app.collectors.web_scraper import WebScraperCollector


@dataclass
class CollectorConfig:
    """Конфигурация коллектора"""
    name: str
    enabled: bool = True
    max_results: int = 50
    priority: int = 1  # 1 = высший приоритет
    config: Dict[str, Any] = None


class CollectorManager:
    """Менеджер для управления всеми коллекторами данных"""
    
    def __init__(self):
        self.collectors: Dict[str, Type[BaseCollector]] = {
            'google': GoogleSearchCollector,
            'yandex': YandexSearchCollector,
            'telegram': TelegramCollector,
            'vkontakte': VKontakteCollector,
            'reddit': RedditCollector,
            'web_scraper': WebScraperCollector,
        }
        
        self.default_configs = {
            'google': CollectorConfig(
                name='google',
                enabled=True,
                max_results=30,
                priority=1
            ),
            'yandex': CollectorConfig(
                name='yandex',
                enabled=True,
                max_results=30,
                priority=2
            ),
            'telegram': CollectorConfig(
                name='telegram',
                enabled=True,
                max_results=20,
                priority=3
            ),
            'vkontakte': CollectorConfig(
                name='vkontakte',
                enabled=True,
                max_results=25,
                priority=4
            ),
            'reddit': CollectorConfig(
                name='reddit',
                enabled=True,
                max_results=25,
                priority=5
            ),
            'web_scraper': CollectorConfig(
                name='web_scraper',
                enabled=True,
                max_results=20,
                priority=6
            ),
        }
    
    async def search_all(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        max_results_per_source: int = 20,
        configs: Optional[Dict[str, CollectorConfig]] = None
    ) -> Dict[str, List[SearchResult]]:
        """
        Поиск по всем или указанным источникам
        
        Args:
            query: Поисковой запрос
            sources: Список источников (если None, используются все доступные)
            max_results_per_source: Максимум результатов с каждого источника
            configs: Пользовательские конфигурации коллекторов
        
        Returns:
            Словарь с результатами по источникам
        """
        if sources is None:
            sources = list(self.collectors.keys())
        
        if configs is None:
            configs = self.default_configs
        
        # Фильтруем только включенные и доступные источники
        active_sources = [
            source for source in sources 
            if source in self.collectors and configs.get(source, self.default_configs.get(source)).enabled
        ]
        
        if not active_sources:
            logger.warning("No active sources for search")
            return {}
        
        # Создаем задачи для асинхронного выполнения
        tasks = []
        for source in active_sources:
            config = configs.get(source, self.default_configs.get(source))
            limit = min(max_results_per_source, config.max_results if config else max_results_per_source)
            
            task = self._search_source(source, query, limit)
            tasks.append((source, task))
        
        # Выполняем все задачи параллельно
        results = {}
        completed_tasks = await asyncio.gather(
            *[task for _, task in tasks],
            return_exceptions=True
        )
        
        for (source, _), result in zip(tasks, completed_tasks):
            if isinstance(result, Exception):
                logger.error(f"Error in {source} collector: {result}")
                results[source] = []
            else:
                results[source] = result
        
        # Логируем статистику
        total_results = sum(len(source_results) for source_results in results.values())
        logger.info(f"Search for '{query}' completed. Total results: {total_results}")
        
        return results
    
    async def _search_source(
        self, 
        source: str, 
        query: str, 
        limit: int
    ) -> List[SearchResult]:
        """Поиск в конкретном источнике"""
        try:
            collector_class = self.collectors[source]
            
            async with collector_class() as collector:
                results = await collector.search(query, limit=limit)
                logger.info(f"{source} search returned {len(results)} results")
                return results
                
        except Exception as e:
            logger.error(f"Error in {source} collector: {e}")
            return []
    
    async def search_combined(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        total_limit: int = 100,
        configs: Optional[Dict[str, CollectorConfig]] = None
    ) -> List[SearchResult]:
        """
        Объединенный поиск по всем источникам с объединением результатов
        
        Args:
            query: Поисковой запрос
            sources: Список источников
            total_limit: Общий лимит результатов
            configs: Конфигурации коллекторов
        
        Returns:
            Список объединенных результатов, отсортированных по релевантности
        """
        # Получаем результаты по источникам
        source_results = await self.search_all(query, sources, total_limit // 3, configs)
        
        # Объединяем все результаты
        all_results = []
        for source, results in source_results.items():
            for result in results:
                # Добавляем информацию об источнике в метаданные
                if result.metadata is None:
                    result.metadata = {}
                result.metadata['search_source'] = source
                all_results.append(result)
        
        # Сортируем результаты (можно улучшить алгоритм ранжирования)
        all_results = self._rank_results(all_results, query)
        
        # Ограничиваем до общего лимита
        return all_results[:total_limit]
    
    def _rank_results(
        self, 
        results: List[SearchResult], 
        query: str
    ) -> List[SearchResult]:
        """
        Ранжирование результатов по релевантности
        """
        query_words = set(query.lower().split())
        
        def calculate_relevance(result: SearchResult) -> float:
            score = 0.0
            
            # Базовый скоринг по содержанию заголовка и текста
            title_words = set(result.title.lower().split()) if result.title else set()
            content_words = set(result.content.lower().split()) if result.content else set()
            
            # Пересечение с запросом
            title_matches = len(query_words.intersection(title_words))
            content_matches = len(query_words.intersection(content_words))
            
            # Заголовок важнее содержания
            score += title_matches * 3.0
            score += content_matches * 1.0
            
            # Бонус за дату публикации (свежие результаты важнее)
            if result.published_at:
                from datetime import datetime, timezone
                days_old = (datetime.now(timezone.utc) - result.published_at).days
                if days_old <= 30:
                    score += 2.0
                elif days_old <= 90:
                    score += 1.0
            
            # Бонус за источник (можно настроить приоритеты)
            source_priority = {
                'google': 1.2,
                'yandex': 1.1,
                'telegram': 1.0,
                'vkontakte': 0.9,
                'reddit': 1.1,
                'web_scraper': 0.8,
            }
            
            source = result.metadata.get('search_source', 'unknown') if result.metadata else 'unknown'
            score *= source_priority.get(source, 1.0)
            
            return score
        
        # Сортируем по релевантности (по убыванию)
        return sorted(results, key=calculate_relevance, reverse=True)
    
    def get_available_sources(self) -> List[str]:
        """Получение списка доступных источников"""
        return list(self.collectors.keys())
    
    def is_source_enabled(self, source: str) -> bool:
        """Проверка, включен ли источник"""
        config = self.default_configs.get(source)
        return config is not None and config.enabled
    
    async def test_sources(self, test_query: str = "python programming") -> Dict[str, bool]:
        """
        Тестирование всех источников
        
        Returns:
            Словарь с результатами тестирования (источник -> успех)
        """
        results = {}
        
        for source in self.collectors.keys():
            try:
                test_results = await self._search_source(source, test_query, limit=1)
                results[source] = len(test_results) > 0
                logger.info(f"Source {source} test: {'PASSED' if results[source] else 'FAILED'}")
                
            except Exception as e:
                results[source] = False
                logger.error(f"Source {source} test failed: {e}")
        
        return results