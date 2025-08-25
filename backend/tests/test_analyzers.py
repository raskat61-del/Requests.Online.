import pytest
from unittest.mock import Mock, patch

from app.analyzers.sentiment import SentimentAnalyzer
from app.analyzers.clustering import TextClusterer
from app.analyzers.frequency import FrequencyAnalyzer


class TestSentimentAnalyzer:
    """Test sentiment analysis functionality"""

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_sentiment_analyzer_initialization(self):
        """Test sentiment analyzer initialization"""
        analyzer = SentimentAnalyzer()
        assert analyzer is not None

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_analyze_positive_sentiment(self, sample_text_data):
        """Test analysis of positive sentiment"""
        analyzer = SentimentAnalyzer()
        
        positive_texts = [
            "I love this product, it's amazing!",
            "Great user interface, very intuitive.",
            "Excellent features and functionality."
        ]
        
        results = await analyzer.analyze(positive_texts)
        
        assert "sentiment_distribution" in results
        assert "average_score" in results
        assert "total_analyzed" in results
        
        # Should detect positive sentiment
        assert results["average_score"] > 0
        assert results["total_analyzed"] == len(positive_texts)

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_analyze_negative_sentiment(self):
        """Test analysis of negative sentiment"""
        analyzer = SentimentAnalyzer()
        
        negative_texts = [
            "This software is terrible, too many bugs.",
            "Poor customer service experience.",
            "The app crashes frequently, very frustrating."
        ]
        
        results = await analyzer.analyze(negative_texts)
        
        # Should detect negative sentiment
        assert results["average_score"] < 0
        assert results["total_analyzed"] == len(negative_texts)

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_analyze_mixed_sentiment(self, sample_text_data):
        """Test analysis of mixed sentiment data"""
        analyzer = SentimentAnalyzer()
        
        results = await analyzer.analyze(sample_text_data)
        
        assert "sentiment_distribution" in results
        distribution = results["sentiment_distribution"]
        
        # Should have all three categories
        assert "positive" in distribution
        assert "negative" in distribution
        assert "neutral" in distribution
        
        # Total should equal input length
        total_count = sum(cat["count"] for cat in distribution.values())
        assert total_count == len(sample_text_data)

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_pain_point_extraction(self):
        """Test pain point extraction from negative sentiment"""
        analyzer = SentimentAnalyzer()
        
        texts_with_pain_points = [
            "The software is too slow and crashes often",
            "Poor customer support, no response to tickets",
            "UI is confusing and hard to navigate",
            "Too many bugs in the latest version",
            "Slow performance issues on mobile devices"
        ]
        
        results = await analyzer.analyze(texts_with_pain_points)
        
        assert "top_pain_points" in results
        pain_points = results["top_pain_points"]
        
        assert len(pain_points) > 0
        
        # Check structure of pain points
        for pain_point in pain_points:
            assert "pain_point" in pain_point
            assert "frequency" in pain_point
            assert isinstance(pain_point["frequency"], int)

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_empty_input(self):
        """Test analyzer with empty input"""
        analyzer = SentimentAnalyzer()
        
        results = await analyzer.analyze([])
        
        assert results["total_analyzed"] == 0
        assert results["average_score"] == 0
        assert results["sentiment_distribution"]["positive"]["count"] == 0

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_russian_text_analysis(self):
        """Test sentiment analysis for Russian text"""
        analyzer = SentimentAnalyzer()
        
        russian_texts = [
            "Это отличный продукт, очень доволен!",
            "Ужасное приложение, много ошибок",
            "Нормальный интерфейс, можно пользоваться"
        ]
        
        results = await analyzer.analyze(russian_texts)
        
        assert results["total_analyzed"] == len(russian_texts)
        assert "sentiment_distribution" in results


class TestTextClusterer:
    """Test text clustering functionality"""

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_clustering_initialization(self):
        """Test clusterer initialization"""
        clusterer = TextClusterer()
        assert clusterer is not None

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_cluster_similar_texts(self):
        """Test clustering of similar texts"""
        clusterer = TextClusterer()
        
        # Create texts with distinct topics
        texts = [
            # Performance issues
            "The app is very slow and takes forever to load",
            "Performance is terrible, loading times are awful",
            "Slow response times, need better performance",
            
            # UI/UX issues
            "The interface is confusing and hard to use",
            "UI design is poor, buttons are not intuitive",
            "User experience is bad, navigation is unclear",
            
            # Bug reports
            "Found several bugs in the latest version",
            "Software crashes frequently, many bugs",
            "Too many errors and bugs in the system"
        ]
        
        results = await clusterer.analyze(texts)
        
        assert "total_clusters" in results
        assert "cluster_details" in results
        assert "avg_cluster_size" in results
        
        clusters = results["cluster_details"]
        assert len(clusters) > 1  # Should find multiple clusters
        
        # Check cluster structure
        for cluster in clusters:
            assert "cluster_id" in cluster
            assert "size" in cluster
            assert "description" in cluster
            assert "keywords" in cluster
            assert isinstance(cluster["keywords"], list)

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_cluster_single_topic(self):
        """Test clustering when all texts are about same topic"""
        clusterer = TextClusterer()
        
        similar_texts = [
            "The application performance is slow",
            "App has slow performance issues",
            "Performance problems with slow loading",
            "Slow app performance needs improvement"
        ]
        
        results = await clusterer.analyze(similar_texts)
        
        # Should create fewer clusters since texts are similar
        assert results["total_clusters"] >= 1
        assert results["avg_cluster_size"] > 1

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_cluster_with_insufficient_data(self):
        """Test clustering with very few texts"""
        clusterer = TextClusterer()
        
        few_texts = ["Single text for testing"]
        
        results = await clusterer.analyze(few_texts)
        
        assert results["total_clusters"] >= 1
        assert len(results["cluster_details"]) >= 1

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_keyword_extraction_from_clusters(self):
        """Test that keywords are properly extracted from clusters"""
        clusterer = TextClusterer()
        
        texts = [
            "Payment processing error occurred during checkout",
            "Credit card payment failed with error message",
            "Payment gateway timeout during transaction processing"
        ]
        
        results = await clusterer.analyze(texts)
        
        clusters = results["cluster_details"]
        
        # Should extract payment-related keywords
        all_keywords = []
        for cluster in clusters:
            all_keywords.extend(cluster["keywords"])
        
        # Should contain payment-related terms
        payment_terms = ["payment", "error", "processing", "failed", "transaction"]
        found_terms = [term for term in payment_terms if any(term in keyword.lower() for keyword in all_keywords)]
        assert len(found_terms) > 0


class TestFrequencyAnalyzer:
    """Test frequency analysis functionality"""

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_frequency_analyzer_initialization(self):
        """Test frequency analyzer initialization"""
        analyzer = FrequencyAnalyzer()
        assert analyzer is not None

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_word_frequency_analysis(self):
        """Test word frequency analysis"""
        analyzer = FrequencyAnalyzer()
        
        texts = [
            "The software has many bugs and performance issues",
            "Performance problems cause user frustration",
            "Software bugs need to be fixed immediately",
            "User interface has performance and usability issues"
        ]
        
        results = await analyzer.analyze(texts)
        
        assert "total_terms" in results
        assert "top_terms" in results
        
        top_terms = results["top_terms"]
        assert len(top_terms) > 0
        
        # Check term structure
        for term in top_terms:
            assert "term" in term
            assert "frequency" in term
            assert "tf_idf_score" in term
            assert isinstance(term["frequency"], int)
            assert isinstance(term["tf_idf_score"], float)
        
        # Should find common terms like "performance", "bugs", etc.
        term_texts = [term["term"].lower() for term in top_terms]
        assert any("performance" in term for term in term_texts)

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_tf_idf_scoring(self):
        """Test TF-IDF scoring functionality"""
        analyzer = FrequencyAnalyzer()
        
        texts = [
            "Unique term appears only here",
            "Common word appears in multiple documents",
            "Common word also appears here with other terms",
            "Another document with common word usage"
        ]
        
        results = await analyzer.analyze(texts)
        
        top_terms = results["top_terms"]
        
        # Terms that appear in fewer documents should have higher TF-IDF scores
        unique_term = next((term for term in top_terms if "unique" in term["term"].lower()), None)
        common_term = next((term for term in top_terms if "common" in term["term"].lower()), None)
        
        if unique_term and common_term:
            assert unique_term["tf_idf_score"] > common_term["tf_idf_score"]

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_stopword_filtering(self):
        """Test that stopwords are properly filtered"""
        analyzer = FrequencyAnalyzer()
        
        texts = [
            "The quick brown fox jumps over the lazy dog",
            "A quick brown fox is jumping over a lazy dog",
            "The fox and the dog are in the same sentence"
        ]
        
        results = await analyzer.analyze(texts)
        
        top_terms = results["top_terms"]
        term_texts = [term["term"].lower() for term in top_terms]
        
        # Common stopwords should not appear in top terms
        stopwords = ["the", "and", "is", "are", "a", "an", "in"]
        for stopword in stopwords:
            assert stopword not in term_texts

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_bigram_trigram_extraction(self):
        """Test extraction of bigrams and trigrams"""
        analyzer = FrequencyAnalyzer()
        
        texts = [
            "Customer service representative was very helpful",
            "Poor customer service experience yesterday",
            "Customer service team needs improvement",
            "Great customer service response time"
        ]
        
        results = await analyzer.analyze(texts)
        
        top_terms = results["top_terms"]
        term_texts = [term["term"] for term in top_terms]
        
        # Should extract "customer service" as a bigram
        bigrams = [term for term in term_texts if len(term.split()) == 2]
        assert len(bigrams) > 0
        assert any("customer service" in bigram.lower() for bigram in bigrams)

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_empty_text_handling(self):
        """Test handling of empty or invalid text"""
        analyzer = FrequencyAnalyzer()
        
        empty_texts = ["", "   ", None]
        # Filter out None values as they wouldn't be in real data
        clean_texts = [text for text in empty_texts if text is not None]
        
        results = await analyzer.analyze(clean_texts)
        
        assert results["total_terms"] == 0
        assert len(results["top_terms"]) == 0

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    async def test_category_assignment(self):
        """Test automatic category assignment for terms"""
        analyzer = FrequencyAnalyzer()
        
        texts = [
            "Login authentication failed with error",
            "Payment processing gateway timeout",
            "User interface design is confusing",
            "Database performance optimization needed"
        ]
        
        results = await analyzer.analyze(texts)
        
        top_terms = results["top_terms"]
        
        # Check that terms have categories assigned
        for term in top_terms:
            assert "category" in term
            assert isinstance(term["category"], str)
        
        # Should categorize technical terms appropriately
        categories = set(term["category"] for term in top_terms)
        assert len(categories) > 0  # Should have at least one category


class TestAnalyzerIntegration:
    """Test integration between different analyzers"""

    @pytest.mark.asyncio
    @pytest.mark.analyzers
    @pytest.mark.integration
    async def test_combined_analysis_workflow(self, sample_text_data):
        """Test running multiple analyzers on same data"""
        sentiment_analyzer = SentimentAnalyzer()
        clusterer = TextClusterer()
        frequency_analyzer = FrequencyAnalyzer()
        
        # Run all analyzers
        sentiment_results = await sentiment_analyzer.analyze(sample_text_data)
        cluster_results = await clusterer.analyze(sample_text_data)
        frequency_results = await frequency_analyzer.analyze(sample_text_data)
        
        # All should process same amount of data
        assert sentiment_results["total_analyzed"] == len(sample_text_data)
        assert len(cluster_results["cluster_details"]) > 0
        assert frequency_results["total_terms"] > 0
        
        # Results should be combinable
        combined_results = {
            "sentiment": sentiment_results,
            "clustering": cluster_results,
            "frequency": frequency_results
        }
        
        assert "sentiment" in combined_results
        assert "clustering" in combined_results
        assert "frequency" in combined_results