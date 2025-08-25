"""
Text Analysis Module for Analytics Bot

This module contains various text analyzers:
- Sentiment Analysis: Analyzes emotional tone of texts
- Clustering Analysis: Groups texts by topic similarity  
- Frequency Analysis: Analyzes keyword and phrase frequencies
"""

from .base import BaseTextAnalyzer, AnalysisResult, ClusterResult, FrequencyResult, TextProcessor
from .sentiment import SentimentAnalyzer
from .clustering import ClusteringAnalyzer
from .frequency import FrequencyAnalyzer

__all__ = [
    "BaseTextAnalyzer",
    "AnalysisResult",
    "ClusterResult", 
    "FrequencyResult",
    "TextProcessor",
    "SentimentAnalyzer",
    "ClusteringAnalyzer",
    "FrequencyAnalyzer"
]