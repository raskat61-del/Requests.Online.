from typing import List, Optional
from datetime import datetime
import json
from loguru import logger

from app.collectors.base import BaseCollector, SearchResult
from app.core.config import settings


class YandexSearchCollector(BaseCollector):
    """Коллектор для Yandex Search API"""
    
    def __init__(self):
        super().__init__()
        self.api_key = settings.YANDEX_API_KEY
        self.base_url = "https://yandex.com/search/xml"
        self.source_type = "yandex"
    
    async def search(
        self, 
        query: str, 
        limit: int = 10,
        language: str = "ru",
        domain: str = "ru",
        **kwargs
    ) -> List[SearchResult]:
        """
        Поиск через Yandex XML API
        
        Args:
            query: Поисковой запрос
            limit: Максимальное количество результатов
            language: Язык интерфейса
            domain: Домен поиска
        """
        if not self.api_key:
            logger.error("Yandex API key not configured")
            return []
        
        results = []
        
        # Yandex API может возвращать до 100 результатов за запрос
        # но лучше делать запросы по частям для стабильности
        page_size = min(50, limit)
        num_pages = (limit + page_size - 1) // page_size
        
        for page in range(num_pages):
            offset = page * page_size
            current_limit = min(page_size, limit - len(results))
            
            params = {
                'apikey': self.api_key,
                'query': query,
                'l10n': language,
                'sortby': 'rlv',  # По релевантности
                'filter': 'moderate',  # Умеренная фильтрация
                'maxpassages': 3,  # Количество отрывков
                'groupby': f'attr=.mode=flat.groups-on-page={current_limit}.docs-in-group=1',
                'page': offset
            }
            
            try:
                # Yandex API требует GET запрос
                response = await self.safe_request(
                    self.base_url,
                    params=params
                )
                
                if not response:
                    break
                
                # Yandex возвращает XML, но можем попробовать JSON API
                content_type = response.headers.get('content-type', '')
                
                if 'xml' in content_type:
                    # Парсим XML ответ
                    xml_content = await response.text()
                    search_results = self._parse_xml_response(xml_content)
                else:
                    # Парсим JSON ответ (если доступен)
                    data = await response.json()
                    search_results = self._parse_json_response(data)
                
                results.extend(search_results)
                
                if len(results) >= limit:
                    break
                    
                # Если получили меньше результатов, чем ожидали, прерываем
                if len(search_results) < current_limit:
                    break
                    
            except Exception as e:
                logger.error(f"Error in Yandex search: {e}")
                break
        
        # Ограничиваем результаты до запрошенного лимита
        results = results[:limit]
        
        logger.info(f"Yandex search for '{query}' returned {len(results)} results")
        return results
    
    def _parse_xml_response(self, xml_content: str) -> List[SearchResult]:
        """Парсинг XML ответа от Yandex"""
        try:
            import xml.etree.ElementTree as ET
            
            root = ET.fromstring(xml_content)
            results = []
            
            # Ищем все элементы doc в response/results/grouping/group/doc
            for group in root.findall('.//group'):
                for doc in group.findall('doc'):
                    result = self._parse_doc_element(doc)
                    if result:
                        results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing Yandex XML response: {e}")
            return []
    
    def _parse_json_response(self, data: dict) -> List[SearchResult]:
        """Парсинг JSON ответа от Yandex (если доступен)"""
        try:
            results = []
            
            # Структура может отличаться в зависимости от версии API
            items = data.get('results', {}).get('items', [])
            
            for item in items:
                result = self._parse_json_item(item)
                if result:
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error parsing Yandex JSON response: {e}")
            return []
    
    def _parse_doc_element(self, doc) -> Optional[SearchResult]:
        """Парсинг элемента doc из XML"""
        try:
            # Извлекаем URL
            url = doc.get('url', '')
            
            # Извлекаем заголовок
            title_elem = doc.find('title')
            title = title_elem.text if title_elem is not None else ''
            
            # Извлекаем содержимое из passages
            content_parts = []
            for passage in doc.findall('.//passage'):
                if passage.text:
                    content_parts.append(passage.text)
            
            content = ' '.join(content_parts)
            
            # Извлекаем домен
            domain_elem = doc.find('domain')
            domain = domain_elem.text if domain_elem is not None else ''
            
            # Создаем метаданные
            metadata_info = self.extract_metadata_info({
                'domain': domain,
                'charset': doc.get('charset'),
                'size': doc.get('size')
            })
            
            return SearchResult(
                title=self.clean_text(title),
                content=self.clean_text(content),
                url=url,
                metadata_info=metadata_info,
                source_type=self.source_type
            )
            
        except Exception as e:
            logger.error(f"Error parsing Yandex doc element: {e}")
            return None
    
    def _parse_json_item(self, item: dict) -> Optional[SearchResult]:
        """Парсинг элемента из JSON ответа"""
        try:
            title = item.get('title', '')
            url = item.get('url', '')
            snippet = item.get('snippet', '')
            
            metadata_info = self.extract_metadata_info(item)
            
            return SearchResult(
                title=self.clean_text(title),
                content=self.clean_text(snippet),
                url=url,
                metadata_info=metadata_info,
                source_type=self.source_type
            )
            
        except Exception as e:
            logger.error(f"Error parsing Yandex JSON item: {e}")
            return None
    
    async def search_by_site(
        self,
        query: str,
        site: str,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Поиск по конкретному сайту
        """
        site_query = f"{query} site:{site}"
        return await self.search(query=site_query, limit=limit)
    
    async def search_recent(
        self,
        query: str,
        limit: int = 10,
        days: int = 30
    ) -> List[SearchResult]:
        """
        Поиск свежих результатов
        """
        # Добавляем фильтр по времени в запрос
        time_query = f"{query} &within={days}"
        return await self.search(query=time_query, limit=limit)