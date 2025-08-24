from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import aiohttp
from abc import ABC, abstractmethod
from dataclasses import dataclass
import re
from urllib.parse import urlparse
from loguru import logger

from app.core.config import settings


@dataclass
class SearchResult:
    title: str
    content: str
    url: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    source_type: str = "unknown"


class BaseCollector(ABC):
    """Базовый класс для всех коллекторов данных"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=settings.TIMEOUT)
        self.headers = {
            'User-Agent': settings.USER_AGENT
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers=self.headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def search(
        self, 
        query: str, 
        limit: int = 10, 
        **kwargs
    ) -> List[SearchResult]:
        """Основной метод поиска"""
        pass
    
    async def safe_request(
        self,
        url: str,
        method: str = 'GET',
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Optional[aiohttp.ClientResponse]:
        """Безопасный HTTP запрос с обработкой ошибок"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        
        for attempt in range(settings.MAX_RETRIES):
            try:
                await asyncio.sleep(settings.REQUEST_DELAY)
                
                async with self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    headers=request_headers
                ) as response:
                    if response.status == 200:
                        return response
                    elif response.status == 429:  # Rate limit
                        logger.warning(f"Rate limit hit for {url}, attempt {attempt + 1}")
                        await asyncio.sleep(2 ** attempt)
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        
            except Exception as e:
                logger.error(f"Request error for {url}, attempt {attempt + 1}: {e}")
                if attempt < settings.MAX_RETRIES - 1:
                    await asyncio.sleep(2 ** attempt)
        
        return None
    
    def clean_text(self, text: str) -> str:
        """Очистка текста"""
        if not text:
            return ""
        
        # Удаляем HTML теги
        text = re.sub(r'<[^>]+>', '', text)
        
        # Удаляем лишние пробелы
        text = re.sub(r'\s+', ' ', text)
        
        # Убираем пробелы по краям
        text = text.strip()
        
        return text
    
    def extract_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Извлечение метаданных"""
        metadata = {}
        
        # Извлекаем домен
        if 'url' in data:
            parsed_url = urlparse(data['url'])
            metadata['domain'] = parsed_url.netloc
        
        # Добавляем остальные данные
        for key, value in data.items():
            if key not in ['title', 'content', 'url', 'author', 'published_at']:
                metadata[key] = value
        
        return metadata