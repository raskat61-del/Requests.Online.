from typing import List, Optional, Dict, Any, Set
from datetime import datetime
from urllib.parse import urljoin, urlparse
import re
import asyncio
from loguru import logger

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    logger.warning("BeautifulSoup4 not available. Install with: pip install beautifulsoup4")

from app.collectors.base import BaseCollector, SearchResult
from app.core.config import settings


class WebScraperCollector(BaseCollector):
    """Collector for web scraping forums and websites"""
    
    def __init__(self):
        super().__init__()
        self.source_type = "web_scraper"
        self.visited_urls: Set[str] = set()
        
        if not BS4_AVAILABLE:
            raise ImportError("BeautifulSoup4 is required for web scraping")
        
        # Common forum platforms and their selectors
        self.forum_selectors = {
            "phpbb": {
                "post_selector": ".post",
                "title_selector": ".topic-title, h2 a",
                "content_selector": ".content, .postbody",
                "author_selector": ".author, .username",
                "date_selector": ".postdate, .post-time"
            },
            "vbulletin": {
                "post_selector": ".postbit, .post",
                "title_selector": ".threadtitle, h1",
                "content_selector": ".postcontent, .post_message",
                "author_selector": ".username, .bigusername",
                "date_selector": ".postdate, .date"
            },
            "discourse": {
                "post_selector": ".topic-post, article",
                "title_selector": ".topic-title, h1",
                "content_selector": ".cooked, .post-body",
                "author_selector": ".username, .names",
                "date_selector": ".post-date, .relative-age"
            },
            "generic": {
                "post_selector": "article, .post, .message, .comment",
                "title_selector": "h1, h2, h3, .title, .subject",
                "content_selector": ".content, .text, .body, .message-body, p",
                "author_selector": ".author, .username, .user, .name",
                "date_selector": ".date, .time, .timestamp, time"
            }
        }
    
    async def search(
        self, 
        query: str, 
        limit: int = 10,
        target_urls: Optional[List[str]] = None,
        max_depth: int = 2,
        **kwargs
    ) -> List[SearchResult]:
        """
        Search web pages and forums
        
        Args:
            query: Search query
            limit: Maximum number of results
            target_urls: List of URLs to scrape
            max_depth: Maximum depth for crawling
        """
        if not target_urls:
            # Default forums and websites to scrape
            target_urls = [
                "https://www.sql.ru/forum/",
                "https://cyber-forum.ru/",
                "https://stackoverflow.com/search?q=" + query.replace(" ", "+"),
                "https://habr.com/ru/search/?q=" + query.replace(" ", "+"),
                "https://toster.ru/search?q=" + query.replace(" ", "+")
            ]
        
        results = []
        
        for url in target_urls:
            try:
                url_results = await self._scrape_url(url, query, limit // len(target_urls) + 1)
                results.extend(url_results)
                
                if len(results) >= limit:
                    break
                    
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                continue
        
        # Sort by relevance and limit results
        results = self._rank_by_relevance(results, query)
        
        logger.info(f"Web scraping for '{query}' returned {len(results)} results")
        return results[:limit]
    
    async def _scrape_url(
        self, 
        url: str, 
        query: str, 
        limit: int
    ) -> List[SearchResult]:
        """Scrape content from a specific URL"""
        if url in self.visited_urls:
            return []
        
        self.visited_urls.add(url)
        results = []
        
        try:
            response = await self.safe_request(url)
            if not response:
                return []
            
            html_content = await response.text()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Detect forum type
            forum_type = self._detect_forum_type(soup, url)
            selectors = self.forum_selectors.get(forum_type, self.forum_selectors["generic"])
            
            # Extract posts/articles
            posts = soup.select(selectors["post_selector"])
            
            query_words = set(query.lower().split())
            
            for post in posts[:limit * 2]:  # Get more posts to filter
                try:
                    result = self._parse_post(post, selectors, url, query_words)
                    if result:
                        results.append(result)
                        
                        if len(results) >= limit:
                            break
                            
                except Exception as e:
                    logger.error(f"Error parsing post: {e}")
                    continue
            
            # If we didn't find enough results, try searching for links to follow
            if len(results) < limit:
                links = await self._find_relevant_links(soup, url, query)
                for link in links[:5]:  # Don't follow too many links
                    if len(results) >= limit:
                        break
                    
                    try:
                        link_results = await self._scrape_url(link, query, limit - len(results))
                        results.extend(link_results)
                    except:
                        continue
        
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {e}")
        
        return results
    
    def _detect_forum_type(self, soup: BeautifulSoup, url: str) -> str:
        """Detect the type of forum/website"""
        
        # Check for specific platform indicators
        if soup.find(class_=re.compile(r'phpbb|forumlist|forum-category')):
            return "phpbb"
        elif soup.find(class_=re.compile(r'vbulletin|postbit|threadbit')):
            return "vbulletin"
        elif soup.find(class_=re.compile(r'discourse|topic-post')) or 'discourse' in url:
            return "discourse"
        elif 'stackoverflow.com' in url or 'stackexchange.com' in url:
            return "stackoverflow"
        elif 'habr.com' in url:
            return "habr"
        else:
            return "generic"
    
    def _parse_post(
        self, 
        post_element, 
        selectors: Dict[str, str], 
        base_url: str,
        query_words: Set[str]
    ) -> Optional[SearchResult]:
        """Parse a single post/article element"""
        try:
            # Extract title
            title_element = post_element.select_one(selectors["title_selector"])
            title = title_element.get_text(strip=True) if title_element else ""
            
            # Extract content
            content_elements = post_element.select(selectors["content_selector"])
            content_parts = []
            for elem in content_elements:
                text = elem.get_text(strip=True)
                if text and len(text) > 10:  # Filter out very short text
                    content_parts.append(text)
            
            content = " ".join(content_parts)
            
            # Check if content is relevant to query
            content_lower = content.lower()
            title_lower = title.lower()
            
            relevance_score = 0
            for word in query_words:
                if word in title_lower:
                    relevance_score += 3
                if word in content_lower:
                    relevance_score += 1
            
            # Skip if not relevant enough
            if relevance_score < 1:
                return None
            
            # Extract author
            author_element = post_element.select_one(selectors["author_selector"])
            author = author_element.get_text(strip=True) if author_element else None
            
            # Extract date
            published_at = None
            date_element = post_element.select_one(selectors["date_selector"])
            if date_element:
                date_text = date_element.get_text(strip=True)
                published_at = self._parse_date(date_text)
            
            # Get URL (try to find a link to the specific post)
            link_element = post_element.find('a', href=True)
            if link_element:
                url = urljoin(base_url, link_element['href'])
            else:
                url = base_url
            
            # Create metadata
            metadata = self.extract_metadata({
                "base_url": base_url,
                "forum_type": self._detect_forum_type(BeautifulSoup(str(post_element), 'html.parser'), base_url),
                "relevance_score": relevance_score,
                "content_length": len(content),
                "has_author": author is not None,
                "has_date": published_at is not None
            })
            
            return SearchResult(
                title=self.clean_text(title) or "Web Content",
                content=self.clean_text(content),
                url=url,
                author=author,
                published_at=published_at,
                metadata=metadata,
                source_type=self.source_type
            )
            
        except Exception as e:
            logger.error(f"Error parsing post element: {e}")
            return None
    
    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse date from various formats"""
        if not date_text:
            return None
        
        # Common date patterns
        patterns = [
            r'(\d{1,2})[./](\d{1,2})[./](\d{4})',  # dd/mm/yyyy or mm/dd/yyyy
            r'(\d{4})[.-](\d{1,2})[.-](\d{1,2})',  # yyyy-mm-dd
            r'(\d{1,2})\s+(янв|фев|мар|апр|мая|июн|июл|авг|сен|окт|ноя|дек)\s+(\d{4})',  # Russian months
            r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})',  # English months
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_text, re.IGNORECASE)
            if match:
                try:
                    # This is a simplified date parser
                    # In production, you'd want more robust date parsing
                    groups = match.groups()
                    if len(groups) == 3:
                        # Try to create a datetime object
                        # This is a basic implementation
                        return datetime.now()  # Placeholder
                except:
                    continue
        
        return None
    
    async def _find_relevant_links(
        self, 
        soup: BeautifulSoup, 
        base_url: str, 
        query: str
    ) -> List[str]:
        """Find links that might contain relevant content"""
        links = []
        query_words = set(query.lower().split())
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            link_text = link.get_text(strip=True).lower()
            
            # Check if link text is relevant
            if any(word in link_text for word in query_words):
                full_url = urljoin(base_url, href)
                
                # Filter out non-content links
                if self._is_content_link(full_url):
                    links.append(full_url)
        
        return links[:10]  # Limit number of links to follow
    
    def _is_content_link(self, url: str) -> bool:
        """Check if URL likely contains content worth scraping"""
        parsed = urlparse(url)
        
        # Skip certain file types and external links
        skip_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar'}
        if any(url.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Skip common non-content pages
        skip_paths = {'login', 'register', 'admin', 'api', 'ajax', 'css', 'js', 'images'}
        if any(skip in parsed.path.lower() for skip in skip_paths):
            return False
        
        return True
    
    def _rank_by_relevance(
        self, 
        results: List[SearchResult], 
        query: str
    ) -> List[SearchResult]:
        """Rank results by relevance to query"""
        query_words = set(query.lower().split())
        
        def calculate_score(result: SearchResult) -> float:
            score = 0.0
            
            title_words = set(result.title.lower().split()) if result.title else set()
            content_words = set(result.content.lower().split()) if result.content else set()
            
            # Title matches are more important
            title_matches = len(query_words.intersection(title_words))
            content_matches = len(query_words.intersection(content_words))
            
            score += title_matches * 3.0
            score += content_matches * 1.0
            
            # Bonus for recent content
            if result.published_at:
                days_old = (datetime.now() - result.published_at).days
                if days_old <= 30:
                    score += 1.0
                elif days_old <= 90:
                    score += 0.5
            
            # Bonus for longer, more detailed content
            if result.content:
                content_length = len(result.content)
                if content_length > 500:
                    score += 0.5
                if content_length > 1000:
                    score += 0.5
            
            return score
        
        return sorted(results, key=calculate_score, reverse=True)
    
    async def scrape_stackoverflow(self, query: str, limit: int = 20) -> List[SearchResult]:
        """Specialized scraping for StackOverflow"""
        search_url = f"https://stackoverflow.com/search?q={query.replace(' ', '+')}"
        return await self._scrape_url(search_url, query, limit)
    
    async def scrape_habr(self, query: str, limit: int = 20) -> List[SearchResult]:
        """Specialized scraping for Habr.com"""
        search_url = f"https://habr.com/ru/search/?q={query.replace(' ', '+')}"
        return await self._scrape_url(search_url, query, limit)