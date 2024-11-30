import re
import logging
from typing import List, Optional, Union
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import re
import unicodedata
import numpy as np
from typing import List


class ElegantTitleGenerator:
    """Generates concise and elegant titles with advanced NLP techniques."""

    def __init__(self):
        """Initialize with NLTK resources and stop words."""
        nltk.download("punkt", quiet=True)
        nltk.download("stopwords", quiet=True)
        self.stop_words = set(stopwords.words("english"))

    def generate_elegant_title(self, titles: List[str], max_length: int = 80) -> str:
        """
        Create an elegant, compact title with key information.

        Args:
            titles: List of raw titles
            max_length: Maximum title length

        Returns:
            Refined, concise title
        """
        # Remove duplicates and clean titles
        unique_titles = list(
            dict.fromkeys(self._clean_title(title) for title in titles)
        )

        # Extract key entities and important words
        key_entities = self._extract_key_entities(unique_titles)

        # Construct elegant title
        elegant_title = self._construct_title(key_entities)

        return elegant_title

    def _clean_title(self, title: str) -> str:
        """
        Clean and normalize title.

        Args:
            title: Raw title string

        Returns:
            Cleaned title
        """
        # Remove special characters, extra spaces
        cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", title)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned.lower()

    def _extract_key_entities(self, titles: List[str]) -> List[str]:
        """
        Extract most significant words from titles.

        Args:
            titles: List of cleaned titles

        Returns:
            List of key entities/words
        """
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(titles)

        # Get feature names (words)
        feature_names = vectorizer.get_feature_names_out()

        # Sum TF-IDF scores across all titles
        tfidf_scores = tfidf_matrix.sum(axis=0).A1

        # Sort words by importance
        sorted_indices = tfidf_scores.argsort()[::-1]
        top_words = [feature_names[i] for i in sorted_indices[:5]]

        return top_words

    def _construct_title(
        self,
        key_entities: List[str],
    ) -> str:
        """
        Construct a title from key entities.

        Args:
            key_entities: Most important words
            max_length: Maximum title length

        Returns:
            Constructed title
        """
        # Capitalize and join key entities
        title_parts = [word.capitalize() for word in key_entities]

        # Create title with smart truncation
        full_title = " ".join(title_parts)
        return full_title.strip()
