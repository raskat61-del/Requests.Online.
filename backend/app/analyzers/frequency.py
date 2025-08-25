from typing import List, Dict, Any, Optional, Tuple, Set
import re
import asyncio
from collections import Counter
import math
from loguru import logger

try:
    from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. Install with: pip install scikit-learn")

from app.analyzers.base import BaseTextAnalyzer, AnalysisResult, FrequencyResult


class FrequencyAnalyzer(BaseTextAnalyzer):
    """Analyzer for frequency analysis of words, phrases, and topics"""
    
    def __init__(self):
        super().__init__()
        self.vectorizer = None
        self.tfidf_vectorizer = None
        
        # Pain point keywords in Russian and English
        self.pain_keywords = {
            'problem': ['проблема', 'проблемы', 'сложность', 'трудность', 'problem', 'issue', 'trouble', 'difficulty'],
            'error': ['ошибка', 'ошибки', 'баг', 'глюк', 'error', 'bug', 'crash', 'fail', 'failure'],
            'slow': ['медленно', 'тормозит', 'лагает', 'виснет', 'slow', 'laggy', 'freezing', 'hang'],
            'need': ['нужно', 'необходимо', 'требуется', 'хочется', 'need', 'want', 'require', 'wish'],
            'help': ['помощь', 'помогите', 'подскажите', 'help', 'assist', 'support'],
            'complaint': ['жалоба', 'недовольство', 'плохо', 'ужасно', 'complaint', 'bad', 'terrible', 'awful']
        }
        
        # Solution keywords
        self.solution_keywords = {
            'solution': ['решение', 'решить', 'исправить', 'solution', 'solve', 'fix', 'resolve'],
            'improvement': ['улучшение', 'улучшить', 'оптимизация', 'improvement', 'optimize', 'enhance'],
            'feature': ['функция', 'возможность', 'фича', 'feature', 'functionality', 'capability'],
            'tool': ['инструмент', 'сервис', 'программа', 'tool', 'service', 'software', 'app'],
            'method': ['способ', 'метод', 'подход', 'method', 'way', 'approach', 'technique']
        }
    
    async def _load_resources(self):
        """Initialize frequency analysis components"""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available, using basic frequency analysis")
            return
        
        # Russian and English stop words
        stop_words = [
            # Russian stop words
            'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так',
            'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было',
            'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг',
            'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж',
            'вам', 'ведь', 'там', 'потом', 'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где', 'есть',
            'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего',
            'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда', 'кто', 'этот', 'того', 'потому', 'этого',
            'какой', 'совсем', 'ним', 'здесь', 'этом', 'один', 'почти', 'мой', 'тем', 'чтобы', 'нее',
            # English stop words
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself',
            'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself',
            'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
            'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because',
            'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after',
            'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further',
            'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
            'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
            'than', 'too', 'very', 'can', 'will', 'just', 'should', 'now'
        ]
        
        # Count vectorizer for basic frequency
        self.vectorizer = CountVectorizer(
            max_features=2000,
            stop_words=stop_words,
            ngram_range=(1, 3),  # Unigrams, bigrams, and trigrams
            min_df=2,  # Ignore terms that appear in less than 2 documents
            max_df=0.95,  # Ignore terms that appear in more than 95% of documents
            lowercase=True,
            token_pattern=r'[а-яёa-z]{2,}'  # Russian and English words only
        )
        
        # TF-IDF vectorizer for weighted frequencies
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=2000,
            stop_words=stop_words,
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.95,
            lowercase=True,
            token_pattern=r'[а-яёa-z]{2,}'
        )
        
        logger.info("Frequency analyzer initialized successfully")
    
    async def analyze_text(self, text: str, text_id: str = None) -> AnalysisResult:
        """Individual text analysis for frequency is handled in analyze_frequency method"""
        keywords = self.extract_keywords(text, top_k=10)
        pain_points = self.detect_pain_points(text)
        
        return AnalysisResult(
            text_id=text_id or "unknown",
            keywords=keywords,
            pain_points=pain_points,
            metadata={'text_length': len(text)}
        )
    
    async def analyze_frequency(
        self,
        texts: List[Tuple[str, str]],  # (text, text_id) pairs
        top_k: int = 50,
        include_ngrams: bool = True,
        categorize_terms: bool = True
    ) -> List[FrequencyResult]:
        """
        Analyze frequency of terms across texts
        
        Args:
            texts: List of (text, text_id) pairs
            top_k: Number of top terms to return
            include_ngrams: Whether to include n-grams (phrases)
            categorize_terms: Whether to categorize terms by type
        
        Returns:
            List of FrequencyResult objects
        """
        if not self._initialized:
            await self.initialize()
        
        if len(texts) < 1:
            logger.warning("Need at least 1 text for frequency analysis")
            return []
        
        logger.info(f"Starting frequency analysis for {len(texts)} texts")
        
        # Preprocess texts
        processed_texts = []
        text_ids = []
        
        for text, text_id in texts:
            processed_text = self.preprocess_text(text)
            if processed_text:
                processed_texts.append(processed_text)
                text_ids.append(text_id)
        
        if not processed_texts:
            logger.warning("No valid texts after preprocessing")
            return []
        
        frequency_results = []
        
        if SKLEARN_AVAILABLE and self.vectorizer and self.tfidf_vectorizer:
            # Use scikit-learn for advanced analysis
            frequency_results = await self._analyze_with_sklearn(
                processed_texts, top_k, categorize_terms
            )
        else:
            # Use basic frequency analysis
            frequency_results = await self._analyze_basic_frequency(
                processed_texts, top_k, include_ngrams, categorize_terms
            )
        
        logger.info(f"Frequency analysis completed: {len(frequency_results)} terms analyzed")
        return frequency_results
    
    async def _analyze_with_sklearn(
        self,
        texts: List[str],
        top_k: int,
        categorize_terms: bool
    ) -> List[FrequencyResult]:
        """Analyze using scikit-learn vectorizers"""
        results = []
        
        try:
            # Fit count vectorizer
            count_matrix = self.vectorizer.fit_transform(texts)
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Fit TF-IDF vectorizer
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            tfidf_feature_names = self.tfidf_vectorizer.get_feature_names_out()
            
            # Calculate frequencies
            frequencies = np.asarray(count_matrix.sum(axis=0)).flatten()
            tfidf_scores = np.asarray(tfidf_matrix.sum(axis=0)).flatten()
            
            # Calculate document frequencies
            doc_frequencies = np.asarray((count_matrix > 0).sum(axis=0)).flatten()
            
            # Create results
            for i, term in enumerate(feature_names):
                frequency = int(frequencies[i])
                
                # Find corresponding TF-IDF score
                tfidf_score = 0.0
                if term in tfidf_feature_names:
                    tfidf_idx = list(tfidf_feature_names).index(term)
                    tfidf_score = float(tfidf_scores[tfidf_idx])
                
                doc_count = int(doc_frequencies[i])
                
                # Categorize term if requested
                category = None
                if categorize_terms:
                    category = self._categorize_term(term)
                
                result = FrequencyResult(
                    term=term,
                    frequency=frequency,
                    tf_idf_score=tfidf_score,
                    document_count=doc_count,
                    category=category
                )
                results.append(result)
            
            # Sort by frequency and take top k
            results.sort(key=lambda x: x.frequency, reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in sklearn frequency analysis: {e}")
            return []
    
    async def _analyze_basic_frequency(
        self,
        texts: List[str],
        top_k: int,
        include_ngrams: bool,
        categorize_terms: bool
    ) -> List[FrequencyResult]:
        """Basic frequency analysis without sklearn"""
        term_counts = Counter()
        doc_counts = Counter()
        total_docs = len(texts)
        
        # Count terms across all texts
        for text in texts:
            words = text.split()
            unique_terms_in_doc = set()
            
            # Count unigrams
            for word in words:
                if len(word) > 2:  # Filter short words
                    term_counts[word] += 1
                    unique_terms_in_doc.add(word)
            
            # Count bigrams and trigrams if requested
            if include_ngrams:
                for i in range(len(words) - 1):
                    bigram = f"{words[i]} {words[i+1]}"
                    if len(bigram) > 5:  # Filter short phrases
                        term_counts[bigram] += 1
                        unique_terms_in_doc.add(bigram)
                
                for i in range(len(words) - 2):
                    trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
                    if len(trigram) > 8:  # Filter short phrases
                        term_counts[trigram] += 1
                        unique_terms_in_doc.add(trigram)
            
            # Count document frequencies
            for term in unique_terms_in_doc:
                doc_counts[term] += 1
        
        # Calculate TF-IDF manually
        results = []
        for term, frequency in term_counts.most_common(top_k * 2):  # Get more to filter later
            doc_count = doc_counts[term]
            
            # Simple TF-IDF calculation
            tf = frequency
            idf = math.log(total_docs / doc_count) if doc_count > 0 else 0
            tf_idf_score = tf * idf
            
            # Filter terms that appear in too many documents (likely stop words)
            if doc_count / total_docs > 0.8:
                continue
            
            category = None
            if categorize_terms:
                category = self._categorize_term(term)
            
            result = FrequencyResult(
                term=term,
                frequency=frequency,
                tf_idf_score=tf_idf_score,
                document_count=doc_count,
                category=category
            )
            results.append(result)
        
        return results[:top_k]
    
    def _categorize_term(self, term: str) -> Optional[str]:
        """Categorize a term based on its semantic meaning"""
        term_lower = term.lower()
        
        # Check pain point categories
        for category, keywords in self.pain_keywords.items():
            if any(keyword in term_lower for keyword in keywords):
                return f"pain_{category}"
        
        # Check solution categories
        for category, keywords in self.solution_keywords.items():
            if any(keyword in term_lower for keyword in keywords):
                return f"solution_{category}"
        
        # Technology categories
        tech_keywords = {
            'programming': ['программирование', 'код', 'programming', 'code', 'development'],
            'database': ['база данных', 'sql', 'database', 'mysql', 'postgresql'],
            'web': ['веб', 'сайт', 'web', 'website', 'html', 'css', 'javascript'],
            'mobile': ['мобильный', 'приложение', 'mobile', 'app', 'android', 'ios'],
            'ai': ['ии', 'искусственный интеллект', 'ai', 'machine learning', 'neural']
        }
        
        for category, keywords in tech_keywords.items():
            if any(keyword in term_lower for keyword in keywords):
                return f"tech_{category}"
        
        return "general"
    
    async def analyze_keyword_trends(
        self,
        frequency_results: List[FrequencyResult],
        min_frequency: int = 5
    ) -> Dict[str, Any]:
        """Analyze trends in keyword usage"""
        if not frequency_results:
            return {}
        
        # Filter by minimum frequency
        filtered_results = [r for r in frequency_results if r.frequency >= min_frequency]
        
        # Group by category
        categories = {}
        for result in filtered_results:
            category = result.category or "uncategorized"
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        # Calculate category statistics
        category_stats = {}
        for category, results in categories.items():
            total_frequency = sum(r.frequency for r in results)
            avg_tfidf = sum(r.tf_idf_score for r in results) / len(results)
            top_terms = sorted(results, key=lambda x: x.frequency, reverse=True)[:5]
            
            category_stats[category] = {
                'term_count': len(results),
                'total_frequency': total_frequency,
                'avg_tf_idf': avg_tfidf,
                'top_terms': [{'term': r.term, 'frequency': r.frequency} for r in top_terms]
            }
        
        # Overall statistics
        total_terms = len(filtered_results)
        total_frequency = sum(r.frequency for r in filtered_results)
        avg_frequency = total_frequency / total_terms if total_terms > 0 else 0
        
        # Top terms overall
        top_terms = sorted(filtered_results, key=lambda x: x.frequency, reverse=True)[:10]
        
        # Most important terms by TF-IDF
        top_tfidf_terms = sorted(filtered_results, key=lambda x: x.tf_idf_score, reverse=True)[:10]
        
        return {
            'total_terms': total_terms,
            'total_frequency': total_frequency,
            'average_frequency': avg_frequency,
            'categories': category_stats,
            'top_terms_by_frequency': [
                {'term': r.term, 'frequency': r.frequency, 'category': r.category}
                for r in top_terms
            ],
            'top_terms_by_tfidf': [
                {'term': r.term, 'tf_idf_score': r.tf_idf_score, 'category': r.category}
                for r in top_tfidf_terms
            ],
            'pain_point_terms': [
                r.term for r in filtered_results 
                if r.category and r.category.startswith('pain_')
            ][:10],
            'solution_terms': [
                r.term for r in filtered_results 
                if r.category and r.category.startswith('solution_')
            ][:10]
        }
    
    async def compare_frequency_distributions(
        self,
        results1: List[FrequencyResult],
        results2: List[FrequencyResult],
        label1: str = "Dataset 1",
        label2: str = "Dataset 2"
    ) -> Dict[str, Any]:
        """Compare frequency distributions between two datasets"""
        # Create term sets
        terms1 = {r.term: r.frequency for r in results1}
        terms2 = {r.term: r.frequency for r in results2}
        
        all_terms = set(terms1.keys()) | set(terms2.keys())
        
        # Find common and unique terms
        common_terms = set(terms1.keys()) & set(terms2.keys())
        unique_to_1 = set(terms1.keys()) - set(terms2.keys())
        unique_to_2 = set(terms2.keys()) - set(terms1.keys())
        
        # Calculate differences for common terms
        frequency_changes = []
        for term in common_terms:
            freq1 = terms1[term]
            freq2 = terms2[term]
            change = freq2 - freq1
            relative_change = (change / freq1 * 100) if freq1 > 0 else 0
            
            frequency_changes.append({
                'term': term,
                'freq_1': freq1,
                'freq_2': freq2,
                'absolute_change': change,
                'relative_change': relative_change
            })
        
        # Sort by absolute change
        frequency_changes.sort(key=lambda x: abs(x['absolute_change']), reverse=True)
        
        return {
            'comparison_summary': {
                'total_terms_1': len(terms1),
                'total_terms_2': len(terms2),
                'common_terms': len(common_terms),
                'unique_to_1': len(unique_to_1),
                'unique_to_2': len(unique_to_2)
            },
            'common_terms': list(common_terms)[:20],
            'unique_to_1': list(unique_to_1)[:20],
            'unique_to_2': list(unique_to_2)[:20],
            'biggest_changes': frequency_changes[:10],
            'emerging_terms': [
                {'term': term, 'frequency': terms2[term]}
                for term in sorted(unique_to_2, key=lambda x: terms2[x], reverse=True)[:10]
            ],
            'declining_terms': [
                {'term': term, 'frequency': terms1[term]}
                for term in sorted(unique_to_1, key=lambda x: terms1[x], reverse=True)[:10]
            ]
        }