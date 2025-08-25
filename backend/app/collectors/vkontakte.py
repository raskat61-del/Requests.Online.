from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from loguru import logger

from app.collectors.base import BaseCollector, SearchResult
from app.core.config import settings


class VKontakteCollector(BaseCollector):
    """Collector for VKontakte social network"""
    
    def __init__(self):
        super().__init__()
        self.access_token = settings.VK_API_TOKEN
        self.api_version = "5.131"
        self.base_url = "https://api.vk.com/method"
        self.source_type = "vkontakte"
    
    async def search(
        self, 
        query: str, 
        limit: int = 10,
        search_type: str = "posts",  # posts, groups, users
        sort_by: str = "date",  # date, likes, comments
        **kwargs
    ) -> List[SearchResult]:
        """
        Search in VKontakte
        
        Args:
            query: Search query
            limit: Maximum number of results
            search_type: Type of search (posts, groups, users)
            sort_by: Sort criteria
        """
        if not self.access_token:
            logger.error("VK API token not configured")
            return []
        
        if search_type == "posts":
            return await self._search_posts(query, limit, sort_by)
        elif search_type == "groups":
            return await self._search_groups(query, limit)
        elif search_type == "users":
            return await self._search_users(query, limit)
        else:
            logger.error(f"Unknown search type: {search_type}")
            return []
    
    async def _search_posts(
        self, 
        query: str, 
        limit: int, 
        sort_by: str = "date"
    ) -> List[SearchResult]:
        """Search posts on VKontakte"""
        results = []
        
        # VK API returns maximum 200 posts per request
        offset = 0
        per_request = min(200, limit)
        
        while len(results) < limit:
            params = {
                "q": query,
                "count": per_request,
                "offset": offset,
                "extended": 1,
                "sort": 2 if sort_by == "date" else 0,  # 2 = by date, 0 = by relevance
                "access_token": self.access_token,
                "v": self.api_version
            }
            
            try:
                response = await self.safe_request(
                    f"{self.base_url}/newsfeed.search",
                    params=params
                )
                
                if not response:
                    break
                
                data = await response.json()
                
                if "error" in data:
                    logger.error(f"VK API error: {data['error']}")
                    break
                
                if "response" not in data or "items" not in data["response"]:
                    break
                
                items = data["response"]["items"]
                profiles = {p["id"]: p for p in data["response"].get("profiles", [])}
                groups = {g["id"]: g for g in data["response"].get("groups", [])}
                
                for item in items:
                    result = self._parse_post(item, profiles, groups)
                    if result:
                        results.append(result)
                
                if len(items) < per_request:
                    break
                
                offset += per_request
                
            except Exception as e:
                logger.error(f"Error searching VK posts: {e}")
                break
        
        logger.info(f"VK posts search for '{query}' returned {len(results)} results")
        return results[:limit]
    
    async def _search_groups(self, query: str, limit: int) -> List[SearchResult]:
        """Search groups on VKontakte"""
        results = []
        
        params = {
            "q": query,
            "count": min(1000, limit),
            "sort": 6,  # Sort by member count
            "access_token": self.access_token,
            "v": self.api_version
        }
        
        try:
            response = await self.safe_request(
                f"{self.base_url}/groups.search",
                params=params
            )
            
            if not response:
                return []
            
            data = await response.json()
            
            if "error" in data:
                logger.error(f"VK API error: {data['error']}")
                return []
            
            if "response" not in data or "items" not in data["response"]:
                return []
            
            for item in data["response"]["items"]:
                result = self._parse_group(item)
                if result:
                    results.append(result)
            
        except Exception as e:
            logger.error(f"Error searching VK groups: {e}")
        
        return results[:limit]
    
    def _parse_post(
        self, 
        item: Dict[str, Any], 
        profiles: Dict[int, Dict], 
        groups: Dict[int, Dict]
    ) -> Optional[SearchResult]:
        """Parse VK post item"""
        try:
            post_id = item.get("id")
            owner_id = item.get("owner_id")
            text = item.get("text", "")
            
            # Get author information
            author = None
            if owner_id > 0:  # User
                profile = profiles.get(owner_id)
                if profile:
                    author = f"{profile.get('first_name', '')} {profile.get('last_name', '')}"
            else:  # Group
                group = groups.get(abs(owner_id))
                if group:
                    author = group.get("name", "")
            
            # Create URL
            url = f"https://vk.com/wall{owner_id}_{post_id}"
            
            # Parse date
            published_at = None
            if "date" in item:
                published_at = datetime.fromtimestamp(item["date"])
            
            # Create title from text preview
            title = f"VK Post: {text[:50]}..." if len(text) > 50 else f"VK Post: {text}"
            
            # Metadata
            metadata = self.extract_metadata({
                "post_id": post_id,
                "owner_id": owner_id,
                "likes": item.get("likes", {}).get("count", 0),
                "reposts": item.get("reposts", {}).get("count", 0),
                "comments": item.get("comments", {}).get("count", 0),
                "views": item.get("views", {}).get("count", 0),
                "post_type": item.get("post_type", ""),
                "is_pinned": item.get("is_pinned", False)
            })
            
            return SearchResult(
                title=self.clean_text(title),
                content=self.clean_text(text),
                url=url,
                author=author,
                published_at=published_at,
                metadata=metadata,
                source_type=self.source_type
            )
            
        except Exception as e:
            logger.error(f"Error parsing VK post: {e}")
            return None
    
    def _parse_group(self, item: Dict[str, Any]) -> Optional[SearchResult]:
        """Parse VK group item"""
        try:
            group_id = item.get("id")
            name = item.get("name", "")
            description = item.get("description", "")
            screen_name = item.get("screen_name", "")
            
            # Create URL
            url = f"https://vk.com/{screen_name}" if screen_name else f"https://vk.com/club{group_id}"
            
            # Create title
            title = f"VK Group: {name}"
            
            # Metadata
            metadata = self.extract_metadata({
                "group_id": group_id,
                "screen_name": screen_name,
                "members_count": item.get("members_count", 0),
                "type": item.get("type", ""),
                "is_closed": item.get("is_closed", 0),
                "verified": item.get("verified", 0),
                "activity": item.get("activity", "")
            })
            
            return SearchResult(
                title=self.clean_text(title),
                content=self.clean_text(description),
                url=url,
                metadata=metadata,
                source_type=self.source_type
            )
            
        except Exception as e:
            logger.error(f"Error parsing VK group: {e}")
            return None
    
    async def search_in_group(
        self, 
        group_id: str, 
        query: str, 
        limit: int = 50
    ) -> List[SearchResult]:
        """Search posts in specific VK group"""
        results = []
        
        # First, get posts from the group
        params = {
            "owner_id": f"-{group_id}" if not group_id.startswith("-") else group_id,
            "count": min(100, limit * 2),  # Get more posts to filter by query
            "extended": 1,
            "access_token": self.access_token,
            "v": self.api_version
        }
        
        try:
            response = await self.safe_request(
                f"{self.base_url}/wall.get",
                params=params
            )
            
            if not response:
                return []
            
            data = await response.json()
            
            if "error" in data:
                logger.error(f"VK API error: {data['error']}")
                return []
            
            if "response" not in data or "items" not in data["response"]:
                return []
            
            items = data["response"]["items"]
            profiles = {p["id"]: p for p in data["response"].get("profiles", [])}
            groups = {g["id"]: g for g in data["response"].get("groups", [])}
            
            # Filter posts by query
            query_words = set(query.lower().split())
            
            for item in items:
                text = item.get("text", "").lower()
                if any(word in text for word in query_words):
                    result = self._parse_post(item, profiles, groups)
                    if result:
                        results.append(result)
                        
                        if len(results) >= limit:
                            break
            
        except Exception as e:
            logger.error(f"Error searching in VK group: {e}")
        
        return results
    
    async def get_trending_posts(self, limit: int = 20) -> List[SearchResult]:
        """Get trending posts from VK"""
        results = []
        
        params = {
            "filters": "post",
            "count": min(100, limit),
            "start_time": int(datetime.now().timestamp()) - 86400,  # Last 24 hours
            "access_token": self.access_token,
            "v": self.api_version
        }
        
        try:
            response = await self.safe_request(
                f"{self.base_url}/newsfeed.get",
                params=params
            )
            
            if not response:
                return []
            
            data = await response.json()
            
            if "error" in data:
                logger.error(f"VK API error: {data['error']}")
                return []
            
            if "response" not in data or "items" not in data["response"]:
                return []
            
            items = data["response"]["items"]
            profiles = {p["id"]: p for p in data["response"].get("profiles", [])}
            groups = {g["id"]: g for g in data["response"].get("groups", [])}
            
            for item in items:
                result = self._parse_post(item, profiles, groups)
                if result:
                    results.append(result)
            
        except Exception as e:
            logger.error(f"Error getting VK trending posts: {e}")
        
        return results[:limit]