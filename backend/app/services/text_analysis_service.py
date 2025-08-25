from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.analyzers.sentiment import SentimentAnalyzer
from app.analyzers.clustering import ClusteringAnalyzer
from app.analyzers.frequency import FrequencyAnalyzer
from app.analyzers.base import AnalysisResult, ClusterResult, FrequencyResult
from app.models.project import Project
from app.models.collected_data import CollectedData
from app.models.analysis import TextAnalysis, Cluster, FrequencyAnalysis


class TextAnalysisService:
    """Service for coordinating text analysis tasks"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sentiment_analyzer = SentimentAnalyzer()
        self.clustering_analyzer = ClusteringAnalyzer()
        self.frequency_analyzer = FrequencyAnalyzer()
    
    async def analyze_project_data(
        self,
        project_id: int,
        analysis_types: Optional[List[str]] = None,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Analyze all collected data for a project
        
        Args:
            project_id: ID of the project to analyze
            analysis_types: Types of analysis to perform ['sentiment', 'clustering', 'frequency']
            batch_size: Batch size for processing
        
        Returns:
            Dictionary with analysis results
        """
        if analysis_types is None:
            analysis_types = ['sentiment', 'clustering', 'frequency']
        
        try:
            # Get project
            project = await self._get_project(project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            # Get collected data
            collected_data = await self._get_collected_data(project_id)
            if not collected_data:
                raise ValueError("No collected data found for analysis")
            
            logger.info(f"Starting text analysis for project {project_id}: {len(collected_data)} documents")
            
            # Prepare text data for analysis
            texts = [(data.content, str(data.id)) for data in collected_data if data.content]
            
            if not texts:
                raise ValueError("No valid text content found for analysis")
            
            results = {
                'project_id': project_id,
                'total_documents': len(collected_data),
                'analyzed_documents': len(texts),
                'analysis_types': analysis_types,
                'started_at': datetime.utcnow().isoformat()
            }
            
            # Perform sentiment analysis
            if 'sentiment' in analysis_types:
                logger.info("Starting sentiment analysis...")
                sentiment_results = await self._perform_sentiment_analysis(texts, batch_size)
                await self._save_sentiment_results(sentiment_results, collected_data)
                results['sentiment'] = await self._summarize_sentiment_results(sentiment_results)
            
            # Perform clustering analysis
            if 'clustering' in analysis_types:
                logger.info("Starting clustering analysis...")
                analysis_results, cluster_results = await self._perform_clustering_analysis(texts)
                await self._save_clustering_results(analysis_results, cluster_results, project_id)
                results['clustering'] = await self._summarize_clustering_results(cluster_results, analysis_results)
            
            # Perform frequency analysis
            if 'frequency' in analysis_types:
                logger.info("Starting frequency analysis...")
                frequency_results = await self._perform_frequency_analysis(texts)
                await self._save_frequency_results(frequency_results, project_id)
                results['frequency'] = await self._summarize_frequency_results(frequency_results)
            
            results['completed_at'] = datetime.utcnow().isoformat()
            results['status'] = 'completed'
            
            logger.info(f"Text analysis completed for project {project_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error in text analysis for project {project_id}: {e}")
            return {
                'project_id': project_id,
                'status': 'failed',
                'error': str(e),
                'failed_at': datetime.utcnow().isoformat()
            }
    
    async def _get_project(self, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_collected_data(self, project_id: int) -> List[CollectedData]:
        """Get all collected data for a project"""
        # Join with search_tasks to filter by project
        from app.models.search_task import SearchTask
        
        result = await self.db.execute(
            select(CollectedData)
            .join(SearchTask)
            .where(SearchTask.project_id == project_id)
            .order_by(CollectedData.created_at)
        )
        return result.scalars().all()
    
    async def _perform_sentiment_analysis(
        self, 
        texts: List[Tuple[str, str]], 
        batch_size: int
    ) -> List[AnalysisResult]:
        """Perform sentiment analysis on texts"""
        return await self.sentiment_analyzer.analyze_batch_sentiment(texts, batch_size)
    
    async def _perform_clustering_analysis(
        self, 
        texts: List[Tuple[str, str]]
    ) -> Tuple[List[AnalysisResult], List[ClusterResult]]:
        """Perform clustering analysis on texts"""
        return await self.clustering_analyzer.cluster_texts(texts, method="auto")
    
    async def _perform_frequency_analysis(
        self, 
        texts: List[Tuple[str, str]]
    ) -> List[FrequencyResult]:
        """Perform frequency analysis on texts"""
        return await self.frequency_analyzer.analyze_frequency(texts, top_k=100)
    
    async def _save_sentiment_results(
        self, 
        results: List[AnalysisResult], 
        collected_data: List[CollectedData]
    ):
        """Save sentiment analysis results to database"""
        data_id_map = {str(data.id): data.id for data in collected_data}
        
        for result in results:
            if result.text_id in data_id_map:
                data_id = data_id_map[result.text_id]
                
                text_analysis = TextAnalysis(
                    data_id=data_id,
                    sentiment_score=result.sentiment_score,
                    sentiment_label=result.sentiment_label,
                    keywords_extracted=result.keywords,
                    pain_points=result.pain_points,
                    confidence_score=result.confidence_score
                )
                self.db.add(text_analysis)
        
        await self.db.commit()
    
    async def _save_clustering_results(
        self, 
        analysis_results: List[AnalysisResult], 
        cluster_results: List[ClusterResult], 
        project_id: int
    ):
        """Save clustering results to database"""
        # Save clusters first
        cluster_id_map = {}
        for cluster_result in cluster_results:
            cluster = Cluster(
                project_id=project_id,
                name=f"Cluster {cluster_result.cluster_id}",
                description=cluster_result.description,
                keywords=cluster_result.keywords,
                size=cluster_result.size,
                avg_sentiment=cluster_result.avg_sentiment
            )
            self.db.add(cluster)
            await self.db.flush()  # Get the ID
            cluster_id_map[cluster_result.cluster_id] = cluster.id
        
        # Update text analysis records with cluster IDs
        for result in analysis_results:
            if result.cluster_id is not None and result.text_id:
                try:
                    data_id = int(result.text_id)
                    cluster_db_id = cluster_id_map.get(result.cluster_id)
                    
                    if cluster_db_id:
                        # Find existing text analysis record
                        existing_analysis = await self.db.execute(
                            select(TextAnalysis).where(TextAnalysis.data_id == data_id)
                        )
                        analysis_record = existing_analysis.scalar_one_or_none()
                        
                        if analysis_record:
                            analysis_record.cluster_id = cluster_db_id
                        else:
                            # Create new record if doesn't exist
                            text_analysis = TextAnalysis(
                                data_id=data_id,
                                cluster_id=cluster_db_id,
                                keywords_extracted=result.keywords,
                                pain_points=result.pain_points
                            )
                            self.db.add(text_analysis)
                except ValueError:
                    logger.error(f"Invalid text_id for clustering: {result.text_id}")
                    continue
        
        await self.db.commit()
    
    async def _save_frequency_results(
        self, 
        results: List[FrequencyResult], 
        project_id: int
    ):
        """Save frequency analysis results to database"""
        for result in results:
            frequency_analysis = FrequencyAnalysis(
                project_id=project_id,
                term=result.term,
                frequency=result.frequency,
                tf_idf_score=result.tf_idf_score,
                document_count=result.document_count,
                category=result.category
            )
            self.db.add(frequency_analysis)
        
        await self.db.commit()
    
    async def _summarize_sentiment_results(
        self, 
        results: List[AnalysisResult]
    ) -> Dict[str, Any]:
        """Create summary of sentiment analysis results"""
        if not results:
            return {}
        
        sentiment_distribution = self.sentiment_analyzer.get_sentiment_distribution(results)
        
        # Extract pain points
        all_pain_points = []
        for result in results:
            if result.pain_points:
                all_pain_points.extend(result.pain_points)
        
        pain_point_freq = {}
        for pain_point in all_pain_points:
            pain_point_freq[pain_point] = pain_point_freq.get(pain_point, 0) + 1
        
        top_pain_points = sorted(pain_point_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_analyzed': len(results),
            'distribution': sentiment_distribution.get('distribution', {}),
            'average_score': sentiment_distribution.get('average_score', 0),
            'score_range': sentiment_distribution.get('score_range', (0, 0)),
            'top_pain_points': [{'pain_point': pp, 'frequency': freq} for pp, freq in top_pain_points],
            'high_confidence_count': len([r for r in results if r.confidence_score and r.confidence_score > 0.7])
        }
    
    async def _summarize_clustering_results(
        self, 
        cluster_results: List[ClusterResult], 
        analysis_results: List[AnalysisResult]
    ) -> Dict[str, Any]:
        """Create summary of clustering results"""
        if not cluster_results:
            return {}
        
        cluster_trends = await self.clustering_analyzer.analyze_cluster_trends(
            cluster_results, analysis_results
        )
        
        # Add cluster details
        cluster_details = []
        for cluster in cluster_results:
            cluster_details.append({
                'cluster_id': cluster.cluster_id,
                'size': cluster.size,
                'keywords': cluster.keywords[:5],  # Top 5 keywords
                'description': cluster.description,
                'avg_sentiment': cluster.avg_sentiment
            })
        
        return {
            'total_clusters': len(cluster_results),
            'cluster_details': cluster_details,
            'trends': cluster_trends,
            'largest_cluster_size': max(c.size for c in cluster_results),
            'smallest_cluster_size': min(c.size for c in cluster_results),
            'avg_cluster_size': sum(c.size for c in cluster_results) / len(cluster_results)
        }
    
    async def _summarize_frequency_results(
        self, 
        results: List[FrequencyResult]
    ) -> Dict[str, Any]:
        """Create summary of frequency analysis results"""
        if not results:
            return {}
        
        keyword_trends = await self.frequency_analyzer.analyze_keyword_trends(results)
        
        # Extract top terms by category
        category_terms = {}
        for result in results:
            category = result.category or 'uncategorized'
            if category not in category_terms:
                category_terms[category] = []
            category_terms[category].append({
                'term': result.term,
                'frequency': result.frequency,
                'tf_idf_score': result.tf_idf_score
            })
        
        # Sort terms in each category
        for category in category_terms:
            category_terms[category].sort(key=lambda x: x['frequency'], reverse=True)
            category_terms[category] = category_terms[category][:10]  # Top 10 per category
        
        return {
            'total_terms': len(results),
            'trends': keyword_trends,
            'by_category': category_terms,
            'top_terms': [
                {
                    'term': r.term,
                    'frequency': r.frequency,
                    'tf_idf_score': r.tf_idf_score,
                    'category': r.category
                }
                for r in results[:20]
            ]
        }
    
    async def get_analysis_results(self, project_id: int) -> Dict[str, Any]:
        """Get existing analysis results for a project"""
        try:
            # Get sentiment analysis results
            sentiment_results = await self.db.execute(
                select(TextAnalysis)
                .join(CollectedData)
                .join(SearchTask)
                .where(SearchTask.project_id == project_id)
            )
            sentiment_data = sentiment_results.scalars().all()
            
            # Get clustering results
            cluster_results = await self.db.execute(
                select(Cluster).where(Cluster.project_id == project_id)
            )
            clusters = cluster_results.scalars().all()
            
            # Get frequency analysis results
            frequency_results = await self.db.execute(
                select(FrequencyAnalysis)
                .where(FrequencyAnalysis.project_id == project_id)
                .order_by(FrequencyAnalysis.frequency.desc())
            )
            frequency_data = frequency_results.scalars().all()
            
            # Compile results
            return {
                'project_id': project_id,
                'sentiment_analysis': {
                    'total_analyzed': len(sentiment_data),
                    'avg_sentiment': sum(s.sentiment_score for s in sentiment_data if s.sentiment_score) / len(sentiment_data) if sentiment_data else 0,
                    'distribution': self._calculate_sentiment_distribution(sentiment_data),
                    'pain_points': self._extract_pain_points_summary(sentiment_data)
                },
                'clustering': {
                    'total_clusters': len(clusters),
                    'clusters': [
                        {
                            'id': c.id,
                            'name': c.name,
                            'size': c.size,
                            'keywords': c.keywords,
                            'description': c.description,
                            'avg_sentiment': c.avg_sentiment
                        }
                        for c in clusters
                    ]
                },
                'frequency_analysis': {
                    'total_terms': len(frequency_data),
                    'top_terms': [
                        {
                            'term': f.term,
                            'frequency': f.frequency,
                            'tf_idf_score': f.tf_idf_score,
                            'category': f.category
                        }
                        for f in frequency_data[:50]
                    ]
                },
                'has_data': len(sentiment_data) > 0 or len(clusters) > 0 or len(frequency_data) > 0
            }
            
        except Exception as e:
            logger.error(f"Error getting analysis results for project {project_id}: {e}")
            return {
                'project_id': project_id,
                'error': str(e),
                'has_data': False
            }
    
    def _calculate_sentiment_distribution(self, sentiment_data: List[TextAnalysis]) -> Dict[str, int]:
        """Calculate sentiment distribution from database records"""
        distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for analysis in sentiment_data:
            if analysis.sentiment_label:
                label = analysis.sentiment_label
                if label in distribution:
                    distribution[label] += 1
        
        return distribution
    
    def _extract_pain_points_summary(self, sentiment_data: List[TextAnalysis]) -> List[Dict[str, Any]]:
        """Extract pain points summary from database records"""
        pain_point_freq = {}
        
        for analysis in sentiment_data:
            if analysis.pain_points:
                for pain_point in analysis.pain_points:
                    pain_point_freq[pain_point] = pain_point_freq.get(pain_point, 0) + 1
        
        sorted_pain_points = sorted(pain_point_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'pain_point': pp, 'frequency': freq}
            for pp, freq in sorted_pain_points[:10]
        ]
    
    async def delete_analysis_results(self, project_id: int) -> bool:
        """Delete all analysis results for a project"""
        try:
            # Delete frequency analysis
            await self.db.execute(
                select(FrequencyAnalysis).where(FrequencyAnalysis.project_id == project_id)
            )
            
            # Delete clusters
            await self.db.execute(
                select(Cluster).where(Cluster.project_id == project_id)
            )
            
            # Delete text analysis (sentiment, etc.)
            from app.models.search_task import SearchTask
            await self.db.execute(
                select(TextAnalysis)
                .join(CollectedData)
                .join(SearchTask)
                .where(SearchTask.project_id == project_id)
            )
            
            await self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting analysis results for project {project_id}: {e}")
            await self.db.rollback()
            return False