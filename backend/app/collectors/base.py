from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import aiohttp
from loguru import logger

from app.core.config import settings


@dataclass
class SearchResult:
    """Класс для представления результата поиска"""
    title: str
    content: str
    url: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    metadata_info: Optional[Dict[str, Any]] = None
    source_type: str = "unknown"


class BaseCollector(ABC):
    """Базовый класс для всех коллекторов данных"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.name = self.__class__.__name__
        self.headers = {
            'User-Agent': settings.USER_AGENT
        }
    
    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=settings.TIMEOUT)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход"""
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
    
    async def rate_limit_delay(self):
        """Задержка для соблюдения rate limits"""
        await asyncio.sleep(settings.REQUEST_DELAY)
    
    async def safe_request(
        self, 
        url: str, 
        method: str = 'GET',
        **kwargs
    ) -> Optional[aiohttp.ClientResponse]:
        """Безопасный HTTP запрос с повторными попытками"""
        for attempt in range(settings.MAX_RETRIES):
            try:
                await self.rate_limit_delay()
                
                if method.upper() == 'GET':
                    response = await self.session.get(url, **kwargs)
                elif method.upper() == 'POST':
                    response = await self.session.post(url, **kwargs)
                else:
                    raise ValueError(f"Неподдерживаемый HTTP метод: {method}")
                
                if response.status == 200:
                    return response
                elif response.status == 429:  # Too Many Requests
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limit hit, waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    
            except Exception as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == settings.MAX_RETRIES - 1:
                    logger.error(f"Max retries reached for {url}")
                    return None
                await asyncio.sleep(2 ** attempt)
        
        return None
    
    def clean_text(self, text: str) -> str:
        """Очистка текста от лишних символов"""
        if not text:
            return ""
        
        # Удаляем лишние пробелы и переносы строк
        text = ' '.join(text.split())
        
        # Ограничиваем длину текста
        max_length = 10000
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text.strip()
    
    def extract_metadata_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Извлечение метаданных из ответа API"""
        return {
            'source': self.name,
            'collected_at': datetime.utcnow().isoformat(),
            'raw_data': data
        }