from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio
import os
from pathlib import Path
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.reports.pdf_generator import PDFReportGenerator
from app.reports.excel_generator import ExcelReportGenerator
from app.reports.base import ReportData
from app.models.project import Project
from app.models.report import Report
from app.services.text_analysis_service import TextAnalysisService
from app.core.config import settings


class ReportService:
    """Service for generating and managing reports"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.generators = {
            'pdf': PDFReportGenerator(),
            'excel': ExcelReportGenerator()
        }
    
    async def generate_report(
        self,
        project_id: int,
        user_id: int,
        report_type: str = "comprehensive",
        format: str = "pdf",
        custom_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a report for a project
        
        Args:
            project_id: ID of the project
            user_id: ID of the user requesting the report
            report_type: Type of report ('comprehensive', 'summary', 'sentiment', 'clustering', 'frequency')
            format: Output format ('pdf', 'excel')
            custom_name: Custom name for the report
        
        Returns:
            Dictionary with report information
        """
        try:
            # Validate format
            if format not in self.generators:
                raise ValueError(f"Unsupported report format: {format}")
            
            # Get project and verify ownership
            project = await self._get_project(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            if project.user_id != user_id:
                raise ValueError("No access to this project")
            
            # Get analysis data
            analysis_service = TextAnalysisService(self.db)
            analysis_data = await analysis_service.get_analysis_results(project_id)
            
            if not analysis_data.get('has_data'):
                raise ValueError("No analysis data available for this project. Please run analysis first.")
            
            # Prepare report data
            report_data = await self._prepare_report_data(
                project, user_id, analysis_data, report_type
            )
            
            # Generate report
            generator = self.generators[format]
            file_path = await generator.generate_report(
                data=report_data,
                template_name=report_type,
                output_filename=custom_name
            )
            
            # Save report record to database
            report_record = await self._save_report_record(
                project_id=project_id,
                name=custom_name or f"{report_type.capitalize()} Report",
                report_type=report_type,
                format=format,
                file_path=file_path
            )
            
            # Get file size
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            logger.info(f"Report generated successfully: {file_path}")
            
            return {
                'status': 'completed',
                'report_id': report_record.id,
                'project_id': project_id,
                'report_type': report_type,
                'format': format,
                'file_path': file_path,
                'file_size': file_size,
                'generated_at': datetime.utcnow().isoformat(),
                'download_url': f"/api/v1/reports/{report_record.id}/download"
            }
            
        except Exception as e:
            logger.error(f"Error generating report for project {project_id}: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'project_id': project_id,
                'failed_at': datetime.utcnow().isoformat()
            }
    
    async def _get_project(self, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()
    
    async def _prepare_report_data(
        self,
        project: Project,
        user_id: int,
        analysis_data: Dict[str, Any],
        report_type: str
    ) -> Dict[str, Any]:
        """Prepare data for report generation"""
        # Get user info
        from app.models.user import User
        user_result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        user_name = user.full_name or user.username if user else "Unknown User"
        
        # Filter analysis data based on report type
        filtered_analysis_data = analysis_data.copy()
        
        if report_type == "sentiment":
            filtered_analysis_data = {
                'sentiment': analysis_data.get('sentiment_analysis', {})
            }
        elif report_type == "clustering":
            filtered_analysis_data = {
                'clustering': analysis_data.get('clustering', {})
            }
        elif report_type == "frequency":
            filtered_analysis_data = {
                'frequency': analysis_data.get('frequency_analysis', {})
            }
        elif report_type == "summary":
            # Include only summary statistics
            filtered_analysis_data = {
                'sentiment': {
                    'total_analyzed': analysis_data.get('sentiment_analysis', {}).get('total_analyzed', 0),
                    'average_score': analysis_data.get('sentiment_analysis', {}).get('avg_sentiment', 0),
                    'distribution': analysis_data.get('sentiment_analysis', {}).get('distribution', {}),
                    'top_pain_points': analysis_data.get('sentiment_analysis', {}).get('pain_points', [])[:5]
                },
                'clustering': {
                    'total_clusters': analysis_data.get('clustering', {}).get('total_clusters', 0),
                    'cluster_details': analysis_data.get('clustering', {}).get('clusters', [])[:5]
                },
                'frequency': {
                    'total_terms': analysis_data.get('frequency_analysis', {}).get('total_terms', 0),
                    'top_terms': analysis_data.get('frequency_analysis', {}).get('top_terms', [])[:10]
                }
            }
        # For 'comprehensive', use all data
        
        return {
            'project_id': project.id,
            'project_name': project.name,
            'user_name': user_name,
            'analysis_data': filtered_analysis_data,
            'metadata': {
                'project_description': project.description,
                'project_status': project.status,
                'created_at': project.created_at.isoformat() if project.created_at else None,
                'updated_at': project.updated_at.isoformat() if project.updated_at else None,
                'report_type': report_type
            }
        }
    
    async def _save_report_record(
        self,
        project_id: int,
        name: str,
        report_type: str,
        format: str,
        file_path: str
    ) -> Report:
        """Save report record to database"""
        # Get file size
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        report = Report(
            project_id=project_id,
            name=name,
            report_type=report_type,
            format=format,
            file_path=file_path,
            file_size=file_size,
            status="completed",
            generated_at=datetime.utcnow(),
            parameters=None  # Could store generation parameters as JSON
        )
        
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        
        return report
    
    async def get_project_reports(
        self, 
        project_id: int, 
        user_id: int
    ) -> List[Dict[str, Any]]:
        """Get all reports for a project"""
        # Verify project ownership
        project = await self._get_project(project_id)
        if not project or project.user_id != user_id:
            raise ValueError("Project not found or no access")
        
        # Get reports
        result = await self.db.execute(
            select(Report)
            .where(Report.project_id == project_id)
            .order_by(Report.generated_at.desc())
        )
        reports = result.scalars().all()
        
        report_list = []
        for report in reports:
            # Check if file still exists
            file_exists = os.path.exists(report.file_path) if report.file_path else False
            
            report_list.append({
                'id': report.id,
                'name': report.name,
                'report_type': report.report_type,
                'format': report.format,
                'file_size': report.file_size,
                'status': report.status,
                'generated_at': report.generated_at.isoformat() if report.generated_at else None,
                'file_exists': file_exists,
                'download_url': f"/api/v1/reports/{report.id}/download" if file_exists else None
            })
        
        return report_list
    
    async def get_report_by_id(
        self, 
        report_id: int, 
        user_id: int
    ) -> Optional[Report]:
        """Get report by ID with ownership verification"""
        result = await self.db.execute(
            select(Report)
            .join(Project)
            .where(
                Report.id == report_id,
                Project.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def delete_report(
        self, 
        report_id: int, 
        user_id: int
    ) -> bool:
        """Delete a report"""
        try:
            # Get report with ownership verification
            report = await self.get_report_by_id(report_id, user_id)
            if not report:
                return False
            
            # Delete file if exists
            if report.file_path and os.path.exists(report.file_path):
                try:
                    os.unlink(report.file_path)
                    logger.info(f"Deleted report file: {report.file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete report file {report.file_path}: {e}")
            
            # Delete database record
            await self.db.delete(report)
            await self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting report {report_id}: {e}")
            await self.db.rollback()
            return False
    
    async def cleanup_old_reports(self, max_age_days: int = 30):
        """Clean up old reports from database and filesystem"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
            
            # Get old reports
            result = await self.db.execute(
                select(Report).where(Report.generated_at < cutoff_date)
            )
            old_reports = result.scalars().all()
            
            deleted_count = 0
            for report in old_reports:
                # Delete file if exists
                if report.file_path and os.path.exists(report.file_path):
                    try:
                        os.unlink(report.file_path)
                    except Exception as e:
                        logger.error(f"Failed to delete old report file {report.file_path}: {e}")
                
                # Delete database record
                await self.db.delete(report)
                deleted_count += 1
            
            await self.db.commit()
            logger.info(f"Cleaned up {deleted_count} old reports")
            
            # Also clean up files in generators
            for generator in self.generators.values():
                await generator.cleanup_old_reports(max_age_days)
                
        except Exception as e:
            logger.error(f"Error during report cleanup: {e}")
            await self.db.rollback()
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported report formats"""
        formats = []
        for generator in self.generators.values():
            formats.extend(generator.get_supported_formats())
        return list(set(formats))
    
    def get_available_report_types(self) -> List[str]:
        """Get list of available report types"""
        return ["comprehensive", "summary", "sentiment", "clustering", "frequency"]