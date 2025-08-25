from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from app.db.database import get_async_session
from app.api.v1.schemas.user import User
from app.core.security import get_current_active_user
from app.services.data_collection_service import DataCollectionService
from app.services.project_service import ProjectService

router = APIRouter()


class StartSearchRequest(BaseModel):
    """Request model for starting search"""
    keyword_ids: Optional[List[int]] = None
    source_names: Optional[List[str]] = None
    max_results_per_source: int = 50


class SearchStatusResponse(BaseModel):
    """Response model for search status"""
    status: str
    total_tasks: int
    status_breakdown: dict
    total_results_collected: int
    last_updated: Optional[str] = None


@router.post("/start/{project_id}")
async def start_search(
    project_id: int,
    request: StartSearchRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Start data collection process for a project"""
    # Verify project ownership
    project_service = ProjectService(db)
    project = await project_service.get_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this project"
        )
    
    # Start data collection
    collection_service = DataCollectionService(db)
    result = await collection_service.start_collection_task(
        project_id=project_id,
        keyword_ids=request.keyword_ids,
        source_names=request.source_names,
        max_results_per_source=request.max_results_per_source
    )
    
    return result


@router.get("/status/{project_id}", response_model=SearchStatusResponse)
async def get_search_status(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get status of data collection for a project"""
    # Verify project ownership
    project_service = ProjectService(db)
    project = await project_service.get_by_id(project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this project"
        )
    
    # Get collection status
    collection_service = DataCollectionService(db)
    status_info = await collection_service.get_collection_status(project_id)
    
    return SearchStatusResponse(**status_info)


@router.get("/test-collectors")
async def test_collectors(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Test all available data collectors"""
    from app.collectors.manager import CollectorManager
    
    collector_manager = CollectorManager()
    test_results = await collector_manager.test_sources("python programming")
    
    return {
        "test_query": "python programming",
        "results": test_results,
        "available_sources": collector_manager.get_available_sources()
    }


@router.get("/sources")
async def get_available_sources(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get list of available data sources"""
    from app.collectors.manager import CollectorManager
    
    collector_manager = CollectorManager()
    sources = collector_manager.get_available_sources()
    
    source_info = {}
    for source in sources:
        config = collector_manager.default_configs.get(source)
        source_info[source] = {
            "enabled": config.enabled if config else False,
            "max_results": config.max_results if config else 0,
            "priority": config.priority if config else 0
        }
    
    return {
        "sources": source_info,
        "total_sources": len(sources)
    }