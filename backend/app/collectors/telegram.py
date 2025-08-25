from typing import List, Optional, Union
from datetime import datetime
import asyncio
from loguru import logger

try:
    from telethon import TelegramClient
    from telethon.errors import SessionPasswordNeededError, FloodWaitError
    from telethon.tl.types import Message, Channel, Chat
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    logger.warning("Telethon not available. Install with: pip install telethon")

from app.collectors.base import BaseCollector, SearchResult
from app.core.config import settings


class TelegramCollector(BaseCollector):
    """Коллектор для Telegram каналов и групп"""
    
    def __init__(self):
        super().__init__()
        self.api_id = settings.TELEGRAM_API_ID
        self.api_hash = settings.TELEGRAM_API_HASH
        self.client: Optional[TelegramClient] = None
        self.source_type = "telegram"
        
        if not TELETHON_AVAILABLE:
            raise ImportError("Telethon is required for Telegram collector")
    
    async def __aenter__(self):
        """Инициализация Telegram клиента"""
        await super().__aenter__()
        
        if not self.api_id or not self.api_hash:
            logger.error("Telegram API ID or Hash not configured")
            return self
        
        try:
            self.client = TelegramClient(
                'analytics_bot_session',
                self.api_id,
                self.api_hash
            )
            
            await self.client.start()
            logger.info("Telegram client started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Telegram client: {e}")
            self.client = None
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие Telegram клиента"""
        if self.client:
            await self.client.disconnect()
        await super().__aexit__(exc_type, exc_val, exc_tb)
    
    async def search(
        self, 
        query: str, 
        limit: int = 10,
        channels: Optional[List[str]] = None,
        **kwargs
    ) -> List[SearchResult]:
        """
        Поиск сообщений в Telegram каналах
        
        Args:
            query: Поисковой запрос
            limit: Максимальное количество результатов
            channels: Список каналов для поиска (по умолчанию используются популярные)
        """
        if not self.client:
            logger.error("Telegram client not initialized")
            return []
        
        if not channels:
            # Список популярных русскоязычных каналов для поиска
            channels = [
                '@tech_stories',
                '@it_manager',
                '@entrepreneurship_ru',
                '@startup_news',
                '@dev_news',
                '@digital_report',
                '@business_ru'
            ]
        
        all_results = []
        
        for channel in channels:
            try:
                channel_results = await self._search_in_channel(
                    channel, query, limit // len(channels) + 1
                )
                all_results.extend(channel_results)
                
                if len(all_results) >= limit:
                    break
                    
            except FloodWaitError as e:
                logger.warning(f"Rate limit for channel {channel}, waiting {e.seconds}s")
                await asyncio.sleep(e.seconds)
                
            except Exception as e:
                logger.error(f"Error searching in channel {channel}: {e}")
                continue
        
        # Ограничиваем результаты и сортируем по дате
        all_results = sorted(all_results, key=lambda x: x.published_at or datetime.min, reverse=True)
        return all_results[:limit]
    
    async def _search_in_channel(
        self, 
        channel: str, 
        query: str, 
        limit: int
    ) -> List[SearchResult]:
        """Поиск в конкретном канале"""
        results = []
        
        try:
            # Получаем объект канала
            entity = await self.client.get_entity(channel)
            
            # Получаем сообщения из канала
            messages = []
            async for message in self.client.iter_messages(entity, limit=500):
                if isinstance(message, Message) and message.text:
                    # Простой поиск по тексту (можно улучшить)
                    if any(word.lower() in message.text.lower() for word in query.split()):
                        messages.append(message)
                        
                        if len(messages) >= limit:
                            break
            
            # Преобразуем сообщения в SearchResult
            for message in messages:
                result = await self._parse_message(message, entity)
                if result:
                    results.append(result)
            
            logger.info(f"Found {len(results)} messages in {channel} for query '{query}'")
            
        except Exception as e:
            logger.error(f"Error in channel {channel}: {e}")
        
        return results
    
    async def _parse_message(
        self, 
        message: Message, 
        entity: Union[Channel, Chat]
    ) -> Optional[SearchResult]:
        """Парсинг сообщения Telegram"""
        try:
            # Заголовок - имя канала или первые слова сообщения
            if hasattr(entity, 'title'):
                title = f"{entity.title}: {message.text[:50]}..."
            else:
                title = message.text[:50] + "..." if len(message.text) > 50 else message.text
            
            # Автор сообщения
            author = None
            if message.from_id:
                try:
                    sender = await self.client.get_entity(message.from_id)
                    if hasattr(sender, 'first_name'):
                        author = getattr(sender, 'first_name', '')
                        if hasattr(sender, 'last_name') and sender.last_name:
                            author += f" {sender.last_name}"
                    elif hasattr(sender, 'title'):
                        author = sender.title
                except:
                    pass
            
            # URL сообщения
            url = f"https://t.me/{entity.username}/{message.id}" if hasattr(entity, 'username') and entity.username else ""
            
            # Метаданные
            metadata = self.extract_metadata({
                'channel_id': entity.id,
                'channel_title': getattr(entity, 'title', ''),
                'channel_username': getattr(entity, 'username', ''),
                'message_id': message.id,
                'views': getattr(message, 'views', 0),
                'forwards': getattr(message, 'forwards', 0),
                'replies': getattr(message, 'replies', {}).get('replies', 0) if hasattr(message, 'replies') and message.replies else 0
            })
            
            return SearchResult(
                title=self.clean_text(title),
                content=self.clean_text(message.text),
                url=url,
                author=author,
                published_at=message.date,
                metadata=metadata,
                source_type=self.source_type
            )
            
        except Exception as e:
            logger.error(f"Error parsing Telegram message: {e}")
            return None
    
    async def search_channels(
        self,
        query: str,
        limit: int = 10
    ) -> List[SearchResult]:
        """Поиск каналов по запросу"""
        if not self.client:
            return []
        
        try:
            # Поиск каналов через глобальный поиск
            results = await self.client.get_dialogs(limit=100)
            
            matching_channels = []
            for dialog in results:
                if hasattr(dialog.entity, 'title') and query.lower() in dialog.entity.title.lower():
                    matching_channels.append(dialog.entity)
                    
                    if len(matching_channels) >= limit:
                        break
            
            # Получаем последние сообщения из найденных каналов
            search_results = []
            for channel in matching_channels:
                try:
                    async for message in self.client.iter_messages(channel, limit=3):
                        if isinstance(message, Message) and message.text:
                            result = await self._parse_message(message, channel)
                            if result:
                                search_results.append(result)
                except:
                    continue
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching Telegram channels: {e}")
            return []
    
    async def get_channel_info(self, channel: str) -> Optional[dict]:
        """Получение информации о канале"""
        if not self.client:
            return None
        
        try:
            entity = await self.client.get_entity(channel)
            
            return {
                'id': entity.id,
                'title': getattr(entity, 'title', ''),
                'username': getattr(entity, 'username', ''),
                'participants_count': getattr(entity, 'participants_count', 0),
                'description': getattr(entity, 'about', ''),
                'verified': getattr(entity, 'verified', False),
                'restricted': getattr(entity, 'restricted', False)
            }
            
        except Exception as e:
            logger.error(f"Error getting channel info for {channel}: {e}")
            return None