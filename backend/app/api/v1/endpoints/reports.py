from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
import os

from app.db.database import get_async_session
from app.api.v1.schemas.user import User
from app.core.security import get_current_active_user
from app.services.report_service import ReportService
from app.services.project_service import ProjectService

router = APIRouter()


class GenerateReportRequest(BaseModel):
    """Request model for generating reports"""
    report_type: str = "comprehensive"  # comprehensive, summary, sentiment, clustering, frequency
    format: str = "pdf"  # pdf, excel
    custom_name: Optional[str] = None


class ReportResponse(BaseModel):
    """Response model for report information"""
    id: int
    name: str
    report_type: str
    format: str
    file_size: Optional[int] = None
    status: str
    generated_at: Optional[str] = None
    file_exists: bool
    download_url: Optional[str] = None


@router.post("/generate/{project_id}")
async def generate_report(
    project_id: int,
    request: GenerateReportRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Generate a report for a project"""
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
    
    # Generate report
    report_service = ReportService(db)
    result = await report_service.generate_report(
        project_id=project_id,
        user_id=current_user.id,
        report_type=request.report_type,
        format=request.format,
        custom_name=request.custom_name
    )
    
    if result.get('status') == 'failed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get('error', 'Report generation failed')
        )
    
    return result


@router.get("/project/{project_id}", response_model=List[ReportResponse])
async def get_project_reports(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get all reports for a project"""
    report_service = ReportService(db)
    
    try:
        reports = await report_service.get_project_reports(project_id, current_user.id)
        return [ReportResponse(**report) for report in reports]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Download a report file"""
    report_service = ReportService(db)
    
    # Get report with ownership verification
    report = await report_service.get_report_by_id(report_id, current_user.id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check if file exists
    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found"
        )
    
    # Determine media type
    media_type = "application/pdf" if report.format == "pdf" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    # Generate download filename
    filename = f"{report.name}.{report.format}"
    
    return FileResponse(
        path=report.file_path,
        media_type=media_type,
        filename=filename
    )