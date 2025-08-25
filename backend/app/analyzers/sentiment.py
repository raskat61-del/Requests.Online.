from typing import Optional, Dict, Any, List, Tuple
import re
import asyncio
from loguru import logger

try:
    from dostoevsky.tokenization import RegexTokenizer
    from dostoevsky.models import FastTextSocialNetworkModel
    DOSTOEVSKY_AVAILABLE = True
except ImportError:
    DOSTOEVSKY_AVAILABLE = False
    logger.warning("Dostoevsky not available. Install with: pip install dostoevsky")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    logger.warning("TextBlob not available. Install with: pip install textblob")

from app.analyzers.base import BaseTextAnalyzer, AnalysisResult


class SentimentAnalyzer(BaseTextAnalyzer):
    """Sentiment analyzer supporting multiple languages and methods"""
    
    def __init__(self):
        super().__init__()
        self.dostoevsky_model = None
        self.tokenizer = None
        
        # Sentiment lexicons
        self.positive_words_ru = {
            'хорошо', 'отлично', 'прекрасно', 'замечательно', 'великолепно', 'потрясающе',
            'нравится', 'люблю', 'классно', 'круто', 'супер', 'идеально', 'лучше',
            'полезно', 'удобно', 'легко', 'быстро', 'эффективно', 'качественно'
        }
        
        self.negative_words_ru = {
            'плохо', 'ужасно', 'отвратительно', 'кошмар', 'катастрофа', 'провал',
            'не нравится', 'ненавижу', 'отстой', 'дерьмо', 'фигня', 'бред',
            'неудобно', 'сложно', 'медленно', 'глючит', 'тормозит', 'проблема'
        }
        
        self.positive_words_en = {
            'good', 'great', 'excellent', 'awesome', 'fantastic', 'amazing',
            'love', 'like', 'perfect', 'wonderful', 'brilliant', 'outstanding',
            'useful', 'helpful', 'easy', 'fast', 'efficient', 'quality'
        }
        
        self.negative_words_en = {
            'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate',
            'dislike', 'worst', 'sucks', 'crap', 'garbage', 'useless',
            'difficult', 'hard', 'slow', 'broken', 'buggy', 'problem'
        }
    
    async def _load_resources(self):
        """Load sentiment analysis models"""
        try:
            if DOSTOEVSKY_AVAILABLE:
                self.tokenizer = RegexTokenizer()
                self.dostoevsky_model = FastTextSocialNetworkModel(tokenizer=self.tokenizer)
                logger.info("Dostoevsky model loaded successfully")
            else:
                logger.warning("Dostoevsky not available, using fallback methods")
        except Exception as e:
            logger.error(f"Failed to load Dostoevsky model: {e}")
            self.dostoevsky_model = None
    
    async def analyze_text(self, text: str, text_id: str = None) -> AnalysisResult:
        """Analyze sentiment of a single text"""
        if not self._initialized:
            await self.initialize()
        
        if not text or not text.strip():
            return AnalysisResult(
                text_id=text_id or "unknown",
                sentiment_score=0.0,
                sentiment_label="neutral",
                confidence_score=0.0
            )
        
        preprocessed_text = self.preprocess_text(text)
        
        # Try multiple sentiment analysis methods
        sentiment_scores = []
        
        # Method 1: Dostoevsky (for Russian text)
        if self.dostoevsky_model and self._contains_cyrillic(text):
            try:
                dostoevsky_score = await self._analyze_with_dostoevsky(text)
                if dostoevsky_score is not None:
                    sentiment_scores.append(('dostoevsky', dostoevsky_score))
            except Exception as e:
                logger.error(f"Error with Dostoevsky analysis: {e}")
        
        # Method 2: TextBlob (for English text)
        if TEXTBLOB_AVAILABLE and self._contains_latin(text):
            try:
                textblob_score = self._analyze_with_textblob(text)
                if textblob_score is not None:
                    sentiment_scores.append(('textblob', textblob_score))
            except Exception as e:
                logger.error(f"Error with TextBlob analysis: {e}")
        
        # Method 3: Lexicon-based analysis (fallback)
        lexicon_score = self._analyze_with_lexicon(preprocessed_text)
        sentiment_scores.append(('lexicon', lexicon_score))
        
        # Combine scores using weighted average
        final_score = self._combine_sentiment_scores(sentiment_scores)
        sentiment_label = self._score_to_label(final_score)
        
        # Extract additional information
        keywords = self.extract_keywords(preprocessed_text, top_k=5)
        pain_points = self.detect_pain_points(text)
        
        # Calculate metadata
        metadata = {
            'text_length': len(text),
            'processed_length': len(preprocessed_text),
            'methods_used': [method for method, _ in sentiment_scores],
            'contains_cyrillic': self._contains_cyrillic(text),
            'contains_latin': self._contains_latin(text),
            'word_count': len(preprocessed_text.split())
        }
        
        result = AnalysisResult(
            text_id=text_id or "unknown",
            sentiment_score=final_score,
            sentiment_label=sentiment_label,
            keywords=keywords,
            pain_points=pain_points,
            metadata=metadata
        )
        
        result.confidence_score = self.calculate_confidence(result)
        
        return result
    
    async def _analyze_with_dostoevsky(self, text: str) -> Optional[float]:
        """Analyze sentiment using Dostoevsky model"""
        try:
            results = self.dostoevsky_model.predict([text], k=3)
            if not results:
                return None
            
            result = results[0]
            
            # Convert Dostoevsky output to score (-1 to 1)
            positive = result.get('positive', 0.0)
            negative = result.get('negative', 0.0)
            neutral = result.get('neutral', 0.0)
            
            # Calculate weighted score
            score = positive - negative
            return max(-1.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Dostoevsky analysis error: {e}")
            return None
    
    def _analyze_with_textblob(self, text: str) -> Optional[float]:
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            # TextBlob polarity is already in range [-1, 1]
            return blob.sentiment.polarity
        except Exception as e:
            logger.error(f"TextBlob analysis error: {e}")
            return None
    
    def _analyze_with_lexicon(self, text: str) -> float:
        """Analyze sentiment using word lexicons"""
        if not text:
            return 0.0
        
        words = text.lower().split()
        positive_count = 0
        negative_count = 0
        
        for word in words:
            if word in self.positive_words_ru or word in self.positive_words_en:
                positive_count += 1
            elif word in self.negative_words_ru or word in self.negative_words_en:
                negative_count += 1
        
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.0
        
        # Calculate score based on ratio
        score = (positive_count - negative_count) / len(words)
        return max(-1.0, min(1.0, score * 10))  # Amplify signal
    
    def _combine_sentiment_scores(self, scores: List[Tuple[str, float]]) -> float:
        """Combine multiple sentiment scores using weighted average"""
        if not scores:
            return 0.0
        
        # Weights for different methods
        weights = {
            'dostoevsky': 0.5,  # Higher weight for specialized Russian model
            'textblob': 0.4,    # Good for English text
            'lexicon': 0.1      # Fallback method
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for method, score in scores:
            weight = weights.get(method, 0.1)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _score_to_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.1:
            return "positive"
        elif score < -0.1:
            return "negative"
        else:
            return "neutral"
    
    def _contains_cyrillic(self, text: str) -> bool:
        """Check if text contains Cyrillic characters"""
        return bool(re.search(r'[а-яё]', text.lower()))
    
    def _contains_latin(self, text: str) -> bool:
        """Check if text contains Latin characters"""
        return bool(re.search(r'[a-z]', text.lower()))
    
    async def analyze_batch_sentiment(
        self, 
        texts: List[Tuple[str, str]], 
        batch_size: int = 50
    ) -> List[AnalysisResult]:
        """Analyze sentiment for multiple texts optimized for batch processing"""
        if not texts:
            return []
        
        if not self._initialized:
            await self.initialize()
        
        results = []
        
        # Process in batches to avoid memory issues
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Process batch
            batch_tasks = []
            for text, text_id in batch:
                task = self.analyze_text(text, text_id)
                batch_tasks.append(task)
            
            # Execute batch
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Error in batch sentiment analysis: {result}")
                    continue
                results.append(result)
            
            # Small delay between batches to prevent overwhelming the system
            if i + batch_size < len(texts):
                await asyncio.sleep(0.1)
        
        return results
    
    def get_sentiment_distribution(self, results: List[AnalysisResult]) -> Dict[str, Any]:
        """Calculate sentiment distribution statistics"""
        if not results:
            return {}
        
        labels = [r.sentiment_label for r in results if r.sentiment_label]
        scores = [r.sentiment_score for r in results if r.sentiment_score is not None]
        
        distribution = {}
        for label in labels:
            distribution[label] = distribution.get(label, 0) + 1
        
        # Convert to percentages
        total = len(labels)
        for label in distribution:
            distribution[label] = {
                'count': distribution[label],
                'percentage': (distribution[label] / total * 100) if total > 0 else 0
            }
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            'distribution': distribution,
            'average_score': avg_score,
            'total_analyzed': total,
            'score_range': (min(scores), max(scores)) if scores else (0, 0)
        }