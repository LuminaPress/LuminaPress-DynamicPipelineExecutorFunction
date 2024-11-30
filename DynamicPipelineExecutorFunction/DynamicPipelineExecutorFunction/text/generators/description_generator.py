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


class EnhancedDescriptionCleaner:
    """
    Advanced text cleaning utility to handle complex word concatenation and formatting issues.
    """

    @staticmethod
    def separate_concatenated_words(text: str) -> str:
        """
        Intelligently separate concatenated words using advanced techniques.

        Args:
            text (str): Input text with potential concatenated words

        Returns:
            str: Text with words properly separated
        """

        def split_camel_case(word: str) -> str:
            """
            Split camelCase and PascalCase words.

            Args:
                word (str): Input word

            Returns:
                str: Separated words
            """
            # Handle special cases like acronyms
            if word.isupper():
                return word

            # Use regex to split camelCase and PascalCase
            word_parts = re.findall(
                r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)|\d+", word
            )
            return " ".join(word_parts)

        # First, normalize unicode characters
        normalized_text = unicodedata.normalize("NFKD", text)

        # Split concatenated words
        words = re.findall(r"\b\w+\b", normalized_text)
        separated_words = [split_camel_case(word) for word in words]

        return " ".join(separated_words)

    @staticmethod
    def clean_description(description: str) -> str:
        """
        Comprehensive description cleaning with advanced techniques.

        Args:
            description (str): Raw description text

        Returns:
            str: Cleaned and processed description
        """
        # Perform initial cleaning steps
        # Remove HTML tags
        description = re.sub(r"<[^>]+>", "", description)

        # Remove URLs
        description = re.sub(r"https?://\S+|www\.\S+", "", description)

        # Remove special characters and extra whitespace
        description = re.sub(r"[^\w\s.,!?]", " ", description)

        # Separate concatenated words
        description = EnhancedDescriptionCleaner.separate_concatenated_words(
            description
        )

        # Normalize whitespace
        description = re.sub(r"\s+", " ", description).strip()

        return description

    @staticmethod
    def remove_near_duplicates(
        descriptions: List[str], similarity_threshold: float = 0.8
    ) -> List[str]:
        """
        Remove semantically similar descriptions with advanced similarity calculation.

        Args:
            descriptions (List[str]): List of description texts
            similarity_threshold (float): Similarity cutoff for duplicates

        Returns:
            List[str]: Unique descriptions
        """

        def calculate_jaccard_similarity(str1: str, str2: str) -> float:
            """
            Calculate Jaccard similarity between two strings.

            Args:
                str1 (str): First string
                str2 (str): Second string

            Returns:
                float: Jaccard similarity score
            """
            # Tokenize and create sets of words
            set1 = set(str1.lower().split())
            set2 = set(str2.lower().split())

            # Calculate Jaccard similarity
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))

            return intersection / union if union > 0 else 0.0

        unique_descriptions = []
        for desc in descriptions:
            # Check similarity against existing descriptions
            is_unique = all(
                calculate_jaccard_similarity(desc, existing) < similarity_threshold
                for existing in unique_descriptions
            )

            if is_unique:
                unique_descriptions.append(desc)

        return unique_descriptions
