from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import re
import asyncio
from loguru import logger

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available. Install with: pip install spacy")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.decomposition import LatentDirichletAllocation
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. Install with: pip install scikit-learn")


@dataclass
class AnalysisResult:
    """Result of text analysis"""
    text_id: str
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    keywords: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    cluster_id: Optional[int] = None
    pain_points: Optional[List[str]] = None
    confidence_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ClusterResult:
    """Result of clustering analysis"""
    cluster_id: int
    size: int
    keywords: List[str]
    avg_sentiment: float
    representative_texts: List[str]
    description: Optional[str] = None


@dataclass
class FrequencyResult:
    """Result of frequency analysis"""
    term: str
    frequency: int
    tf_idf_score: float
    document_count: int
    category: Optional[str] = None


class BaseTextAnalyzer(ABC):
    """Base class for text analyzers"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self._initialized = False
    
    async def initialize(self):
        """Initialize the analyzer (load models, etc.)"""
        if not self._initialized:
            await self._load_resources()
            self._initialized = True
    
    @abstractmethod
    async def _load_resources(self):
        """Load necessary resources (models, dictionaries, etc.)"""
        pass
    
    @abstractmethod
    async def analyze_text(self, text: str, text_id: str = None) -> AnalysisResult:
        """Analyze a single text"""
        pass
    
    async def analyze_batch(
        self, 
        texts: List[Tuple[str, str]], 
        batch_size: int = 100
    ) -> List[AnalysisResult]:
        """Analyze multiple texts in batches"""
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self.analyze_text(text, text_id) for text, text_id in batch],
                return_exceptions=True
            )
            
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Error analyzing text: {result}")
                    continue
                results.append(result)
        
        return results
    
    def preprocess_text(self, text: str) -> str:
        """Basic text preprocessing"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove special characters but keep Russian and English letters
        text = re.sub(r'[^а-яёa-z0-9\s]', ' ', text)
        
        # Remove extra spaces again
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """Extract keywords from text using simple heuristics"""
        if not text:
            return []
        
        # Simple keyword extraction based on word frequency and length
        words = text.split()
        
        # Filter out short words and common stop words
        stop_words = {
            'и', 'в', 'на', 'с', 'по', 'для', 'от', 'до', 'при', 'за', 'под', 'над', 'о', 'об', 'к', 'у',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are'
        }
        
        filtered_words = [
            word for word in words 
            if len(word) > 3 and word not in stop_words
        ]
        
        # Count word frequencies
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top k
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_k]]
    
    def detect_pain_points(self, text: str) -> List[str]:
        """Detect pain points in text using keyword patterns"""
        pain_indicators = [
            # Russian pain point indicators
            r'\b(проблем[аы]|сложност[ьи]|трудност[ьи]|не получается|не работает|ошибк[аи]|багг?[иы]?|не понимаю)\b',
            r'\b(не могу|не знаю|помогите|подскажите|что делать|как исправить|как решить)\b',
            r'\b(медленно|тормозит|виснет|глючит|лагает|не отвечает)\b',
            r'\b(не хватает|нужн[оа]|необходим[оа]|требуется|хочется|желательно)\b',
            
            # English pain point indicators
            r'\b(problem|issue|trouble|difficulty|error|bug|crash|fail)\b',
            r'\b(can\'t|cannot|don\'t know|help|how to|what to do)\b',
            r'\b(slow|laggy|freezing|not working|broken|stuck)\b',
            r'\b(need|want|require|missing|lack)\b'
        ]
        
        pain_points = []
        text_lower = text.lower()
        
        for pattern in pain_indicators:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join(match)
                pain_points.append(match)
        
        return list(set(pain_points))  # Remove duplicates
    
    def calculate_confidence(self, analysis_result: AnalysisResult) -> float:
        """Calculate confidence score for analysis result"""
        confidence = 0.0
        
        # Base confidence from text length
        if analysis_result.metadata and 'text_length' in analysis_result.metadata:
            text_length = analysis_result.metadata['text_length']
            if text_length > 100:
                confidence += 0.3
            elif text_length > 50:
                confidence += 0.2
            else:
                confidence += 0.1
        
        # Confidence from sentiment analysis
        if analysis_result.sentiment_score is not None:
            # Higher confidence for more extreme sentiment scores
            abs_sentiment = abs(analysis_result.sentiment_score)
            confidence += abs_sentiment * 0.3
        
        # Confidence from keywords
        if analysis_result.keywords:
            confidence += min(len(analysis_result.keywords) / 10.0, 0.2)
        
        # Confidence from pain points detection
        if analysis_result.pain_points:
            confidence += min(len(analysis_result.pain_points) / 5.0, 0.2)
        
        return min(confidence, 1.0)


class TextProcessor:
    """Utility class for text processing operations"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{2,}', '.', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        return text.strip()
    
    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        """Extract sentences from text"""
        if not text:
            return []
        
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    @staticmethod
    def calculate_text_stats(text: str) -> Dict[str, Any]:
        """Calculate basic text statistics"""
        if not text:
            return {}
        
        words = text.split()
        sentences = TextProcessor.extract_sentences(text)
        
        return {
            'character_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0
        }