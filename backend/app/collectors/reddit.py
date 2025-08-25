from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from loguru import logger

try:
    import praw
    from praw.models import Submission, Comment
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    logger.warning("PRAW not available. Install with: pip install praw")

from app.collectors.base import BaseCollector, SearchResult
from app.core.config import settings


class RedditCollector(BaseCollector):
    """Collector for Reddit posts and comments"""
    
    def __init__(self):
        super().__init__()
        self.client_id = settings.REDDIT_CLIENT_ID
        self.client_secret = settings.REDDIT_CLIENT_SECRET
        self.user_agent = settings.REDDIT_USER_AGENT
        self.reddit: Optional[praw.Reddit] = None
        self.source_type = "reddit"
        
        if not PRAW_AVAILABLE:
            raise ImportError("PRAW is required for Reddit collector")
    
    async def __aenter__(self):
        """Initialize Reddit client"""
        await super().__aenter__()
        
        if not self.client_id or not self.client_secret:
            logger.error("Reddit client ID or secret not configured")
            return self
        
        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
                read_only=True
            )
            
            # Test connection
            _ = self.reddit.user.me()
            logger.info("Reddit client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {e}")
            self.reddit = None
        
        return self
    
    async def search(
        self, 
        query: str, 
        limit: int = 10,
        sort: str = "relevance",  # relevance, hot, top, new, comments
        time_filter: str = "all",  # all, day, week, month, year
        subreddits: Optional[List[str]] = None,
        **kwargs
    ) -> List[SearchResult]:
        """
        Search Reddit posts
        
        Args:
            query: Search query
            limit: Maximum number of results
            sort: Sort method
            time_filter: Time filter for results
            subreddits: List of subreddits to search in (if None, search all)
        """
        if not self.reddit:
            logger.error("Reddit client not initialized")
            return []
        
        results = []
        
        try:
            if subreddits:
                # Search in specific subreddits
                for subreddit_name in subreddits:
                    try:
                        subreddit = self.reddit.subreddit(subreddit_name)
                        subreddit_results = await self._search_subreddit(
                            subreddit, query, limit // len(subreddits) + 1, sort, time_filter
                        )
                        results.extend(subreddit_results)
                        
                        if len(results) >= limit:
                            break
                            
                    except Exception as e:
                        logger.error(f"Error searching subreddit {subreddit_name}: {e}")
                        continue
            else:
                # Search all Reddit
                search_results = self.reddit.subreddit("all").search(
                    query, 
                    sort=sort,
                    time_filter=time_filter,
                    limit=limit
                )
                
                for submission in search_results:
                    result = self._parse_submission(submission)
                    if result:
                        results.append(result)
        
        except Exception as e:
            logger.error(f"Error searching Reddit: {e}")
        
        logger.info(f"Reddit search for '{query}' returned {len(results)} results")
        return results[:limit]
    
    async def _search_subreddit(
        self,
        subreddit,
        query: str,
        limit: int,
        sort: str,
        time_filter: str
    ) -> List[SearchResult]:
        """Search in specific subreddit"""
        results = []
        
        try:
            search_results = subreddit.search(
                query,
                sort=sort,
                time_filter=time_filter,
                limit=limit
            )
            
            for submission in search_results:
                result = self._parse_submission(submission)
                if result:
                    results.append(result)
                    
        except Exception as e:
            logger.error(f"Error searching subreddit: {e}")
        
        return results
    
    def _parse_submission(self, submission: Submission) -> Optional[SearchResult]:
        """Parse Reddit submission"""
        try:
            # Get submission URL
            url = f"https://reddit.com{submission.permalink}"
            
            # Create title
            title = f"r/{submission.subreddit.display_name}: {submission.title}"
            
            # Get content (selftext for text posts, url for link posts)
            content = submission.selftext if submission.selftext else submission.url
            
            # Parse creation time
            published_at = datetime.fromtimestamp(submission.created_utc)
            
            # Get author
            author = str(submission.author) if submission.author else "[deleted]"
            
            # Create metadata
            metadata_info = self.extract_metadata_info({
                "submission_id": submission.id,
                "subreddit": submission.subreddit.display_name,
                "score": submission.score,
                "upvote_ratio": submission.upvote_ratio,
                "num_comments": submission.num_comments,
                "gilded": submission.gilded,
                "is_self": submission.is_self,
                "is_video": submission.is_video,
                "over_18": submission.over_18,
                "spoiler": submission.spoiler,
                "stickied": submission.stickied,
                "locked": submission.locked,
                "flair_text": submission.link_flair_text,
                "domain": submission.domain if hasattr(submission, 'domain') else None
            })
            
            return SearchResult(
                title=self.clean_text(title),
                content=self.clean_text(content),
                url=url,
                author=author,
                published_at=published_at,
                metadata_info=metadata_info,
                source_type=self.source_type
            )
            
        except Exception as e:
            logger.error(f"Error parsing Reddit submission: {e}")
            return None
    
    async def search_comments(
        self,
        query: str,
        limit: int = 20,
        subreddits: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Search Reddit comments"""
        if not self.reddit:
            return []
        
        results = []
        
        try:
            # Get recent submissions and search their comments
            if subreddits:
                all_subreddits = "+".join(subreddits)
            else:
                all_subreddits = "all"
            
            subreddit = self.reddit.subreddit(all_subreddits)
            
            # Get recent hot submissions
            submissions = list(subreddit.hot(limit=50))
            
            query_words = set(query.lower().split())
            
            for submission in submissions:
                try:
                    # Load comments
                    submission.comments.replace_more(limit=0)
                    
                    for comment in submission.comments.list():
                        if isinstance(comment, Comment) and comment.body:
                            # Check if comment contains query terms
                            comment_text = comment.body.lower()
                            if any(word in comment_text for word in query_words):
                                result = self._parse_comment(comment, submission)
                                if result:
                                    results.append(result)
                                    
                                    if len(results) >= limit:
                                        break
                    
                    if len(results) >= limit:
                        break
                        
                except Exception as e:
                    logger.error(f"Error processing submission comments: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error searching Reddit comments: {e}")
        
        return results[:limit]
    
    def _parse_comment(self, comment: Comment, submission: Submission) -> Optional[SearchResult]:
        """Parse Reddit comment"""
        try:
            # Create URL to comment
            url = f"https://reddit.com{comment.permalink}"
            
            # Create title
            title = f"Comment on: {submission.title[:50]}..."
            
            # Get comment content
            content = comment.body
            
            # Parse creation time
            published_at = datetime.fromtimestamp(comment.created_utc)
            
            # Get author
            author = str(comment.author) if comment.author else "[deleted]"
            
            # Create metadata
            metadata_info = self.extract_metadata_info({
                "comment_id": comment.id,
                "submission_id": submission.id,
                "submission_title": submission.title,
                "subreddit": submission.subreddit.display_name,
                "score": comment.score,
                "gilded": comment.gilded,
                "is_submitter": comment.is_submitter,
                "stickied": comment.stickied,
                "depth": comment.depth if hasattr(comment, 'depth') else 0
            })
            
            return SearchResult(
                title=self.clean_text(title),
                content=self.clean_text(content),
                url=url,
                author=author,
                published_at=published_at,
                metadata_info=metadata_info,
                source_type="reddit_comment"
            )
            
        except Exception as e:
            logger.error(f"Error parsing Reddit comment: {e}")
            return None
    
    async def get_subreddit_posts(
        self,
        subreddit_name: str,
        sort: str = "hot",  # hot, new, top, rising
        limit: int = 25,
        time_filter: str = "day"
    ) -> List[SearchResult]:
        """Get posts from specific subreddit"""
        if not self.reddit:
            return []
        
        results = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            if sort == "hot":
                submissions = subreddit.hot(limit=limit)
            elif sort == "new":
                submissions = subreddit.new(limit=limit)
            elif sort == "top":
                submissions = subreddit.top(time_filter=time_filter, limit=limit)
            elif sort == "rising":
                submissions = subreddit.rising(limit=limit)
            else:
                submissions = subreddit.hot(limit=limit)
            
            for submission in submissions:
                result = self._parse_submission(submission)
                if result:
                    results.append(result)
        
        except Exception as e:
            logger.error(f"Error getting subreddit posts: {e}")
        
        return results
    
    async def search_programming_subreddits(
        self,
        query: str,
        limit: int = 50
    ) -> List[SearchResult]:
        """Search in programming-related subreddits"""
        programming_subreddits = [
            "programming",
            "Python",
            "javascript",
            "webdev",
            "MachineLearning",
            "datascience",
            "artificial",
            "cscareerquestions",
            "learnprogramming",
            "softwaredevelopment",
            "coding",
            "algorithms",
            "compsci"
        ]
        
        return await self.search(
            query=query,
            limit=limit,
            subreddits=programming_subreddits,
            sort="relevance",
            time_filter="month"
        )