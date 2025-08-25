from typing import List, Optional
from datetime import datetime
import json
from loguru import logger

from app.collectors.base import BaseCollector, SearchResult
from app.core.config import settings


class GoogleSearchCollector(BaseCollector):
    """Коллектор для Google Custom Search API"""
    
    def __init__(self):
        super().__init__()
        self.api_key = settings.GOOGLE_API_KEY
        self.cse_id = settings.GOOGLE_CSE_ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.source_type = "google"
    
    async def search(
        self, 
        query: str, 
        limit: int = 10,
        language: str = "lang_ru",
        date_restrict: Optional[str] = None,
        **kwargs
    ) -> List[SearchResult]:
        """
        Поиск через Google Custom Search API
        
        Args:
            query: Поисковой запрос
            limit: Максимальное количество результатов
            language: Язык поиска
            date_restrict: Ограничение по дате (например, 'm1' = последний месяц)
        """
        if not self.api_key or not self.cse_id:
            logger.error("Google API key or CSE ID not configured")
            return []
        
        results = []
        
        # Google API возвращает максимум 10 результатов за запрос
        # Для получения большего количества нужно делать несколько запросов
        num_requests = (limit + 9) // 10  # Округляем вверх
        
        for page in range(num_requests):
            start_index = page * 10 + 1
            
            params = {
                'key': self.api_key,
                'cx': self.cse_id,
                'q': query,
                'start': start_index,
                'num': min(10, limit - len(results)),
                'lr': language,
                'safe': 'off',
                'fields': 'items(title,link,snippet,pagemap,displayLink)'
            }
            
            if date_restrict:
                params['dateRestrict'] = date_restrict
            
            try:
                response = await self.safe_request(
                    self.base_url,
                    params=params
                )
                
                if not response:
                    break
                
                data = await response.json()
                
                if 'items' not in data:
                    logger.warning(f"No items in Google search response for query: {query}")
                    break
                
                for item in data['items']:
                    result = self._parse_search_item(item)
                    if result:
                        results.append(result)
                        
                        if len(results) >= limit:
                            break
                
                # Если получили меньше результатов, чем ожидали, прерываем
                if len(data.get('items', [])) < 10:
                    break
                    
            except Exception as e:
                logger.error(f"Error in Google search: {e}")
                break
        
        logger.info(f"Google search for '{query}' returned {len(results)} results")
        return results
    
    def _parse_search_item(self, item: dict) -> Optional[SearchResult]:
        """Парсинг элемента результата поиска"""
        try:
            title = item.get('title', '')
            url = item.get('link', '')
            snippet = item.get('snippet', '')
            
            # Пытаемся извлечь дополнительную информацию из pagemap
            pagemap = item.get('pagemap', {})
            
            # Извлекаем дату публикации если есть
            published_at = None
            if 'newsarticle' in pagemap:
                date_published = pagemap['newsarticle'][0].get('datepublished')
                if date_published:
                    try:
                        published_at = datetime.fromisoformat(date_published.replace('Z', '+00:00'))
                    except:
                        pass
            
            # Извлекаем автора если есть
            author = None
            if 'newsarticle' in pagemap:
                author = pagemap['newsarticle'][0].get('author')
            elif 'person' in pagemap:
                author = pagemap['person'][0].get('name')
            
            # Создаем метаданные
            metadata_info = self.extract_metadata_info({
                'display_link': item.get('displayLink'),
                'pagemap': pagemap,
                'search_query': item.get('title')
            })
            
            return SearchResult(
                title=self.clean_text(title),
                content=self.clean_text(snippet),
                url=url,
                author=author,
                published_at=published_at,
                metadata_info=metadata_info,
                source_type=self.source_type
            )
            
        except Exception as e:
            logger.error(f"Error parsing Google search item: {e}")
            return None
    
    async def search_news(
        self,
        query: str,
        limit: int = 10,
        sort_by: str = "date"
    ) -> List[SearchResult]:
        """
        Поиск новостей через Google News
        """
        # Добавляем специфичные для новостей параметры
        news_query = f"{query} site:news.google.com OR site:ria.ru OR site:interfax.ru OR site:tass.ru"
        
        return await self.search(
            query=news_query,
            limit=limit,
            date_restrict="m1"  # Последний месяц
        )
    
    async def search_forums(
        self,
        query: str,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Поиск на форумах
        """
        # Добавляем сайты форумов
        forum_query = f"{query} (site:forum.ru OR site:cyber-forum.ru OR site:sql.ru OR inurl:forum OR inurl:phpbb)"
        
        return await self.search(
            query=forum_query,
            limit=limit
        )