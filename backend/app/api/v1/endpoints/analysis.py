from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from app.db.database import get_async_session
from app.api.v1.schemas.user import User
from app.core.security import get_current_active_user
from app.services.text_analysis_service import TextAnalysisService
from app.services.project_service import ProjectService

router = APIRouter()


class AnalysisRequest(BaseModel):
    """Request model for starting analysis"""
    analysis_types: Optional[List[str]] = None  # ['sentiment', 'clustering', 'frequency']
    batch_size: int = 100


class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    project_id: int
    status: str
    total_documents: Optional[int] = None
    analyzed_documents: Optional[int] = None
    sentiment: Optional[dict] = None
    clustering: Optional[dict] = None
    frequency: Optional[dict] = None
    error: Optional[str] = None


@router.post("/start/{project_id}", response_model=AnalysisResponse)
async def start_analysis(
    project_id: int,
    request: AnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Start text analysis for a project"""
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
    
    # Start text analysis
    analysis_service = TextAnalysisService(db)
    result = await analysis_service.analyze_project_data(
        project_id=project_id,
        analysis_types=request.analysis_types,
        batch_size=request.batch_size
    )
    
    return AnalysisResponse(**result)


@router.get("/results/{project_id}", response_model=AnalysisResponse)
async def get_analysis_results(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get text analysis results for a project"""
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
    
    # Get analysis results
    analysis_service = TextAnalysisService(db)
    results = await analysis_service.get_analysis_results(project_id)
    
    if not results.get('has_data'):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis results found for this project"
        )
    
    return AnalysisResponse(
        project_id=project_id,
        status="completed",
        sentiment=results.get('sentiment_analysis'),
        clustering=results.get('clustering'),
        frequency=results.get('frequency_analysis')
    )