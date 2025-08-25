from typing import List, Dict, Any, Optional, Tuple
import asyncio
import numpy as np
from loguru import logger

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.metrics import silhouette_score
    from sklearn.decomposition import TruncatedSVD
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. Install with: pip install scikit-learn")

from app.analyzers.base import BaseTextAnalyzer, AnalysisResult, ClusterResult


class ClusteringAnalyzer(BaseTextAnalyzer):
    """Analyzer for clustering texts by topic/content similarity"""
    
    def __init__(self):
        super().__init__()
        self.vectorizer = None
        self.svd = None
        self.cluster_models = {}
        
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn is required for clustering analysis")
    
    async def _load_resources(self):
        """Initialize clustering components"""
        # Create TF-IDF vectorizer with Russian and English stop words
        russian_stop_words = [
            'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так',
            'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было',
            'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг',
            'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж',
            'вам', 'сказал', 'ведь', 'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где',
            'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб', 'без', 'будто',
            'человек', 'чего', 'раз', 'тоже', 'себе', 'под', 'жизнь', 'будет', 'ж', 'тогда', 'кто', 'этот',
            'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь', 'этом', 'один', 'почти', 'мой',
            'тем', 'чтобы', 'нее', 'кажется', 'сейчас', 'были', 'куда', 'зачем', 'сказать', 'всех', 'никогда',
            'сегодня', 'можно', 'при', 'наконец', 'два', 'об', 'другой', 'хоть', 'после', 'над', 'больше',
            'тот', 'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 'много', 'разве', 'сказала', 'три',
            'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой', 'перед', 'иногда', 'лучше', 'чуть', 'том',
            'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно', 'всю', 'между'
        ]
        
        english_stop_words = [
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself',
            'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
            'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
            'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because',
            'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after',
            'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further',
            'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
            'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
            'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
        ]
        
        combined_stop_words = list(set(russian_stop_words + english_stop_words))
        
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=combined_stop_words,
            ngram_range=(1, 2),  # Include bigrams
            min_df=2,  # Ignore terms that appear in less than 2 documents
            max_df=0.95,  # Ignore terms that appear in more than 95% of documents
            lowercase=True,
            token_pattern=r'[а-яёa-z]{2,}'  # Russian and English words only
        )
        
        # SVD for dimensionality reduction
        self.svd = TruncatedSVD(n_components=50, random_state=42)
        
        logger.info("Clustering analyzer initialized successfully")
    
    async def analyze_text(self, text: str, text_id: str = None) -> AnalysisResult:
        """Individual text analysis for clustering is handled in cluster_texts method"""
        # For clustering, we need multiple texts, so this method returns basic analysis
        keywords = self.extract_keywords(text, top_k=5)
        pain_points = self.detect_pain_points(text)
        
        return AnalysisResult(
            text_id=text_id or "unknown",
            keywords=keywords,
            pain_points=pain_points,
            metadata={'text_length': len(text)}
        )
    
    async def cluster_texts(
        self,
        texts: List[Tuple[str, str]],  # (text, text_id) pairs
        n_clusters: Optional[int] = None,
        method: str = "kmeans",  # kmeans, dbscan, auto
        min_cluster_size: int = 3
    ) -> Tuple[List[AnalysisResult], List[ClusterResult]]:
        """
        Cluster texts and return analysis results
        
        Args:
            texts: List of (text, text_id) pairs
            n_clusters: Number of clusters (if None, will be auto-determined)
            method: Clustering method to use
            min_cluster_size: Minimum cluster size for DBSCAN
        
        Returns:
            Tuple of (analysis_results, cluster_results)
        """
        if not self._initialized:
            await self.initialize()
        
        if len(texts) < 2:
            logger.warning("Need at least 2 texts for clustering")
            return [], []
        
        logger.info(f"Starting clustering analysis for {len(texts)} texts")
        
        # Preprocess texts
        processed_texts = []
        text_ids = []
        
        for text, text_id in texts:
            processed_text = self.preprocess_text(text)
            if processed_text:  # Skip empty texts
                processed_texts.append(processed_text)
                text_ids.append(text_id)
        
        if len(processed_texts) < 2:
            logger.warning("Not enough valid texts after preprocessing")
            return [], []
        
        # Vectorize texts
        try:
            tfidf_matrix = self.vectorizer.fit_transform(processed_texts)
            logger.info(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
        except Exception as e:
            logger.error(f"Error creating TF-IDF matrix: {e}")
            return [], []
        
        # Reduce dimensionality if needed
        if tfidf_matrix.shape[1] > 50:
            try:
                reduced_matrix = self.svd.fit_transform(tfidf_matrix)
                logger.info(f"Reduced matrix shape: {reduced_matrix.shape}")
            except Exception as e:
                logger.error(f"Error in dimensionality reduction: {e}")
                reduced_matrix = tfidf_matrix.toarray()
        else:
            reduced_matrix = tfidf_matrix.toarray()
        
        # Determine optimal number of clusters if not specified
        if n_clusters is None:
            n_clusters = self._determine_optimal_clusters(reduced_matrix, method)
        
        # Perform clustering
        cluster_labels = await self._perform_clustering(
            reduced_matrix, n_clusters, method, min_cluster_size
        )
        
        if cluster_labels is None:
            logger.error("Clustering failed")
            return [], []
        
        # Create analysis results
        analysis_results = []
        for i, (text, text_id) in enumerate(zip(processed_texts, text_ids)):
            if i < len(cluster_labels):
                cluster_id = cluster_labels[i]
                keywords = self.extract_keywords(text, top_k=5)
                pain_points = self.detect_pain_points(text)
                
                result = AnalysisResult(
                    text_id=text_id,
                    keywords=keywords,
                    pain_points=pain_points,
                    cluster_id=int(cluster_id),
                    metadata={
                        'text_length': len(text),
                        'clustering_method': method,
                        'total_clusters': len(set(cluster_labels))
                    }
                )
                analysis_results.append(result)
        
        # Create cluster summaries
        cluster_results = self._create_cluster_summaries(
            processed_texts, text_ids, cluster_labels, tfidf_matrix
        )
        
        logger.info(f"Clustering completed: {len(set(cluster_labels))} clusters created")
        
        return analysis_results, cluster_results
    
    def _determine_optimal_clusters(self, data: np.ndarray, method: str) -> int:
        """Determine optimal number of clusters"""
        n_samples = data.shape[0]
        
        if method == "dbscan":
            # For DBSCAN, we don't need to determine clusters beforehand
            return -1
        
        # For KMeans, use elbow method or silhouette analysis
        max_clusters = min(10, n_samples // 2)
        
        if max_clusters < 2:
            return 2
        
        best_score = -1
        best_k = 2
        
        for k in range(2, max_clusters + 1):
            try:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                labels = kmeans.fit_predict(data)
                
                if len(set(labels)) > 1:  # Ensure we have multiple clusters
                    score = silhouette_score(data, labels)
                    if score > best_score:
                        best_score = score
                        best_k = k
            except Exception as e:
                logger.error(f"Error calculating silhouette score for k={k}: {e}")
                continue
        
        logger.info(f"Optimal number of clusters determined: {best_k} (silhouette score: {best_score:.3f})")
        return best_k
    
    async def _perform_clustering(
        self,
        data: np.ndarray,
        n_clusters: int,
        method: str,
        min_cluster_size: int
    ) -> Optional[np.ndarray]:
        """Perform the actual clustering"""
        try:
            if method == "kmeans":
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                labels = kmeans.fit_predict(data)
                
            elif method == "dbscan":
                # Estimate eps parameter
                from sklearn.neighbors import NearestNeighbors
                neighbors = NearestNeighbors(n_neighbors=min_cluster_size)
                neighbors_fit = neighbors.fit(data)
                distances, indices = neighbors_fit.kneighbors(data)
                distances = np.sort(distances, axis=0)
                eps = np.mean(distances[:, min_cluster_size-1])
                
                dbscan = DBSCAN(eps=eps, min_samples=min_cluster_size)
                labels = dbscan.fit_predict(data)
                
            elif method == "auto":
                # Try both methods and choose the best one
                kmeans_labels = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit_predict(data)
                
                # Try DBSCAN
                from sklearn.neighbors import NearestNeighbors
                neighbors = NearestNeighbors(n_neighbors=min_cluster_size)
                neighbors_fit = neighbors.fit(data)
                distances, indices = neighbors_fit.kneighbors(data)
                distances = np.sort(distances, axis=0)
                eps = np.mean(distances[:, min_cluster_size-1])
                
                dbscan_labels = DBSCAN(eps=eps, min_samples=min_cluster_size).fit_predict(data)
                
                # Choose based on silhouette score
                try:
                    kmeans_score = silhouette_score(data, kmeans_labels) if len(set(kmeans_labels)) > 1 else -1
                    dbscan_score = silhouette_score(data, dbscan_labels) if len(set(dbscan_labels)) > 1 else -1
                    
                    if kmeans_score > dbscan_score:
                        labels = kmeans_labels
                        logger.info(f"Chose KMeans (score: {kmeans_score:.3f})")
                    else:
                        labels = dbscan_labels
                        logger.info(f"Chose DBSCAN (score: {dbscan_score:.3f})")
                except:
                    labels = kmeans_labels  # Fallback
                    
            else:
                raise ValueError(f"Unknown clustering method: {method}")
            
            return labels
            
        except Exception as e:
            logger.error(f"Error in clustering: {e}")
            return None
    
    def _create_cluster_summaries(
        self,
        texts: List[str],
        text_ids: List[str],
        cluster_labels: np.ndarray,
        tfidf_matrix
    ) -> List[ClusterResult]:
        """Create summaries for each cluster"""
        cluster_results = []
        unique_labels = set(cluster_labels)
        
        for cluster_id in unique_labels:
            if cluster_id == -1:  # Noise cluster in DBSCAN
                continue
                
            # Get texts in this cluster
            cluster_mask = cluster_labels == cluster_id
            cluster_texts = [texts[i] for i, mask in enumerate(cluster_mask) if mask]
            cluster_text_ids = [text_ids[i] for i, mask in enumerate(cluster_mask) if mask]
            
            if len(cluster_texts) == 0:
                continue
            
            # Extract cluster keywords using TF-IDF
            cluster_tfidf = tfidf_matrix[cluster_mask]
            cluster_keywords = self._extract_cluster_keywords(cluster_tfidf, top_k=10)
            
            # Calculate average sentiment if available
            avg_sentiment = 0.0  # Would need sentiment analysis results
            
            # Select representative texts (shortest and longest)
            text_lengths = [(i, len(text)) for i, text in enumerate(cluster_texts)]
            text_lengths.sort(key=lambda x: x[1])
            
            representative_texts = []
            if text_lengths:
                # Add shortest text
                representative_texts.append(cluster_texts[text_lengths[0][0]][:200] + "...")
                # Add longest text if different
                if len(text_lengths) > 1:
                    representative_texts.append(cluster_texts[text_lengths[-1][0]][:200] + "...")
            
            # Generate cluster description
            description = self._generate_cluster_description(cluster_keywords, cluster_texts)
            
            cluster_result = ClusterResult(
                cluster_id=int(cluster_id),
                size=len(cluster_texts),
                keywords=cluster_keywords,
                avg_sentiment=avg_sentiment,
                representative_texts=representative_texts,
                description=description
            )
            
            cluster_results.append(cluster_result)
        
        return cluster_results
    
    def _extract_cluster_keywords(self, cluster_tfidf, top_k: int = 10) -> List[str]:
        """Extract top keywords for a cluster using TF-IDF scores"""
        try:
            # Calculate mean TF-IDF scores for the cluster
            mean_scores = np.mean(cluster_tfidf, axis=0).A1
            
            # Get feature names
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Get top keywords
            top_indices = mean_scores.argsort()[-top_k:][::-1]
            keywords = [feature_names[i] for i in top_indices if mean_scores[i] > 0]
            
            return keywords
            
        except Exception as e:
            logger.error(f"Error extracting cluster keywords: {e}")
            return []
    
    def _generate_cluster_description(self, keywords: List[str], texts: List[str]) -> str:
        """Generate a human-readable description for a cluster"""
        if not keywords:
            return "Mixed topics"
        
        # Simple description based on top keywords
        top_keywords = keywords[:3]
        
        if len(top_keywords) == 1:
            return f"Discussions about {top_keywords[0]}"
        elif len(top_keywords) == 2:
            return f"Topics related to {top_keywords[0]} and {top_keywords[1]}"
        else:
            return f"Conversations about {', '.join(top_keywords[:-1])} and {top_keywords[-1]}"
    
    async def analyze_cluster_trends(
        self,
        cluster_results: List[ClusterResult],
        analysis_results: List[AnalysisResult]
    ) -> Dict[str, Any]:
        """Analyze trends and patterns across clusters"""
        if not cluster_results:
            return {}
        
        # Cluster size distribution
        sizes = [cluster.size for cluster in cluster_results]
        
        # Most common keywords across clusters
        all_keywords = []
        for cluster in cluster_results:
            all_keywords.extend(cluster.keywords)
        
        keyword_freq = {}
        for keyword in all_keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Pain points distribution
        pain_points_by_cluster = {}
        for result in analysis_results:
            if result.cluster_id is not None and result.pain_points:
                cluster_id = result.cluster_id
                if cluster_id not in pain_points_by_cluster:
                    pain_points_by_cluster[cluster_id] = []
                pain_points_by_cluster[cluster_id].extend(result.pain_points)
        
        return {
            'total_clusters': len(cluster_results),
            'cluster_sizes': {
                'min': min(sizes),
                'max': max(sizes),
                'avg': sum(sizes) / len(sizes),
                'distribution': sizes
            },
            'top_keywords': top_keywords,
            'pain_points_by_cluster': {
                str(k): list(set(v)) for k, v in pain_points_by_cluster.items()
            },
            'largest_cluster': max(cluster_results, key=lambda x: x.size).cluster_id,
            'most_keywords_cluster': max(cluster_results, key=lambda x: len(x.keywords)).cluster_id
        }