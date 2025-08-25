from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.collectors.manager import CollectorManager, CollectorConfig
from app.collectors.base import SearchResult
from app.models.project import Project
from app.models.keyword import Keyword, SearchSource
from app.models.search_task import SearchTask
from app.models.collected_data import CollectedData
from app.core.config import settings


class DataCollectionService:
    """Service for orchestrating data collection from various sources"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.collector_manager = CollectorManager()
    
    async def start_collection_task(
        self,
        project_id: int,
        keyword_ids: Optional[List[int]] = None,
        source_names: Optional[List[str]] = None,
        max_results_per_source: int = 50
    ) -> Dict[str, Any]:
        """
        Start a data collection task for a project
        
        Args:
            project_id: ID of the project
            keyword_ids: List of keyword IDs to search for (if None, use all active keywords)
            source_names: List of source names to use (if None, use all available)
            max_results_per_source: Maximum results per source per keyword
        
        Returns:
            Dictionary with task information and results
        """
        try:
            # Get project
            project = await self._get_project(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            # Get keywords to search for
            keywords = await self._get_keywords(project_id, keyword_ids)
            if not keywords:
                raise ValueError("No keywords found for collection")
            
            # Get available sources
            sources = await self._get_sources(source_names)
            if not sources:
                raise ValueError("No sources available for collection")
            
            logger.info(f"Starting collection for project {project_id}: {len(keywords)} keywords, {len(sources)} sources")
            
            # Create search tasks
            search_tasks = []
            for keyword in keywords:
                for source in sources:
                    task = SearchTask(
                        project_id=project_id,
                        keyword_id=keyword.id,
                        source_id=source.id,
                        status="pending",
                        scheduled_at=datetime.utcnow()
                    )
                    self.db.add(task)
                    search_tasks.append(task)
            
            await self.db.commit()
            
            # Execute collection tasks
            collection_results = await self._execute_collection_tasks(
                search_tasks, max_results_per_source
            )
            
            # Update task statuses and save results
            total_collected = 0
            for task, results in collection_results.items():
                task.completed_at = datetime.utcnow()
                task.results_count = len(results)
                
                if results:
                    task.status = "completed"
                    total_collected += len(results)
                    
                    # Save collected data
                    for result in results:
                        collected_data = CollectedData(
                            task_id=task.id,
                            source_type=result.source_type,
                            source_url=result.url,
                            title=result.title,
                            content=result.content,
                            author=result.author,
                            published_at=result.published_at,
                            metadata_info=result.metadata_info
                        )
                        self.db.add(collected_data)
                else:
                    task.status = "completed"  # No results but task completed
            
            await self.db.commit()
            
            logger.info(f"Collection completed for project {project_id}: {total_collected} items collected")
            
            return {
                "status": "completed",
                "project_id": project_id,
                "keywords_processed": len(keywords),
                "sources_used": len(sources),
                "tasks_created": len(search_tasks),
                "total_collected": total_collected,
                "collection_summary": self._create_collection_summary(collection_results)
            }
            
        except Exception as e:
            logger.error(f"Error in collection task for project {project_id}: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "project_id": project_id
            }
    
    async def _get_project(self, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_keywords(
        self, 
        project_id: int, 
        keyword_ids: Optional[List[int]] = None
    ) -> List[Keyword]:
        """Get keywords for the project"""
        query = select(Keyword).where(
            and_(
                Keyword.project_id == project_id,
                Keyword.is_active == True
            )
        )
        
        if keyword_ids:
            query = query.where(Keyword.id.in_(keyword_ids))
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def _get_sources(
        self, 
        source_names: Optional[List[str]] = None
    ) -> List[SearchSource]:
        """Get available search sources"""
        query = select(SearchSource).where(SearchSource.is_enabled == True)
        
        if source_names:
            query = query.where(SearchSource.name.in_(source_names))
        
        result = await self.db.execute(query)
        sources = result.scalars().all()
        
        # If no sources in DB, create default ones
        if not sources:
            sources = await self._create_default_sources()
        
        return sources
    
    async def _create_default_sources(self) -> List[SearchSource]:
        """Create default search sources in database"""
        default_sources = [
            {"name": "google", "rate_limit": 100},
            {"name": "yandex", "rate_limit": 100},
            {"name": "telegram", "rate_limit": 50},
            {"name": "vkontakte", "rate_limit": 100},
            {"name": "reddit", "rate_limit": 60},
            {"name": "web_scraper", "rate_limit": 200},
        ]
        
        sources = []
        for source_data in default_sources:
            source = SearchSource(**source_data)
            self.db.add(source)
            sources.append(source)
        
        await self.db.commit()
        return sources
    
    async def _execute_collection_tasks(
        self,
        search_tasks: List[SearchTask],
        max_results_per_source: int
    ) -> Dict[SearchTask, List[SearchResult]]:
        """Execute collection tasks in parallel"""
        results = {}
        
        # Group tasks by source and keyword for efficient processing
        tasks_by_source = {}
        for task in search_tasks:
            source_name = None
            # Get source name (we need to query it)
            # For now, let's use a simple approach
            source_result = await self.db.execute(
                select(SearchSource).where(SearchSource.id == task.source_id)
            )
            source = source_result.scalar_one_or_none()
            if source:
                source_name = source.name
            
            if source_name not in tasks_by_source:
                tasks_by_source[source_name] = []
            tasks_by_source[source_name].append(task)
        
        # Execute collection for each source
        for source_name, source_tasks in tasks_by_source.items():
            if source_name not in self.collector_manager.collectors:
                logger.warning(f"Collector for source {source_name} not available")
                for task in source_tasks:
                    results[task] = []
                continue
            
            try:
                source_results = await self._collect_from_source(
                    source_name, source_tasks, max_results_per_source
                )
                results.update(source_results)
                
            except Exception as e:
                logger.error(f"Error collecting from source {source_name}: {e}")
                for task in source_tasks:
                    results[task] = []
        
        return results
    
    async def _collect_from_source(
        self,
        source_name: str,
        tasks: List[SearchTask],
        max_results_per_source: int
    ) -> Dict[SearchTask, List[SearchResult]]:
        """Collect data from a specific source"""
        results = {}
        
        try:
            collector_class = self.collector_manager.collectors[source_name]
            
            async with collector_class() as collector:
                for task in tasks:
                    # Get keyword text
                    keyword_result = await self.db.execute(
                        select(Keyword).where(Keyword.id == task.keyword_id)
                    )
                    keyword = keyword_result.scalar_one_or_none()
                    
                    if not keyword:
                        results[task] = []
                        continue
                    
                    # Update task status
                    task.status = "running"
                    task.started_at = datetime.utcnow()
                    await self.db.commit()
                    
                    try:
                        # Perform search
                        search_results = await collector.search(
                            keyword.keyword, 
                            limit=max_results_per_source
                        )
                        results[task] = search_results
                        
                        logger.info(f"Collected {len(search_results)} results for keyword '{keyword.keyword}' from {source_name}")
                        
                    except Exception as e:
                        logger.error(f"Error searching keyword '{keyword.keyword}' in {source_name}: {e}")
                        task.error_message = str(e)
                        task.status = "failed"
                        results[task] = []
                    
                    # Rate limiting delay
                    await asyncio.sleep(settings.REQUEST_DELAY)
        
        except Exception as e:
            logger.error(f"Error initializing collector {source_name}: {e}")
            for task in tasks:
                results[task] = []
        
        return results
    
    def _create_collection_summary(
        self, 
        collection_results: Dict[SearchTask, List[SearchResult]]
    ) -> Dict[str, Any]:
        """Create summary of collection results"""
        summary = {
            "by_source": {},
            "by_keyword": {},
            "total_results": 0,
            "successful_tasks": 0,
            "failed_tasks": 0
        }
        
        for task, results in collection_results.items():
            # Count by source
            source_name = "unknown"  # We'd need to fetch this from DB
            if source_name not in summary["by_source"]:
                summary["by_source"][source_name] = 0
            summary["by_source"][source_name] += len(results)
            
            # Count totals
            summary["total_results"] += len(results)
            if results:
                summary["successful_tasks"] += 1
            else:
                summary["failed_tasks"] += 1
        
        return summary
    
    async def get_collection_status(self, project_id: int) -> Dict[str, Any]:
        """Get status of data collection for a project"""
        # Get all search tasks for the project
        result = await self.db.execute(
            select(SearchTask).where(SearchTask.project_id == project_id)
        )
        tasks = result.scalars().all()
        
        if not tasks:
            return {
                "status": "no_tasks",
                "message": "No collection tasks found for this project"
            }
        
        # Analyze task statuses
        status_counts = {}
        total_results = 0
        
        for task in tasks:
            status = task.status
            if status not in status_counts:
                status_counts[status] = 0
            status_counts[status] += 1
            total_results += task.results_count or 0
        
        # Determine overall status
        if status_counts.get("running", 0) > 0:
            overall_status = "running"
        elif status_counts.get("pending", 0) > 0:
            overall_status = "pending"
        elif status_counts.get("failed", 0) == len(tasks):
            overall_status = "failed"
        else:
            overall_status = "completed"
        
        return {
            "status": overall_status,
            "total_tasks": len(tasks),
            "status_breakdown": status_counts,
            "total_results_collected": total_results,
            "last_updated": max(task.completed_at or task.created_at for task in tasks) if tasks else None
        }