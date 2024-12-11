import re
import logging
from typing import List, Optional, Union
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import unicodedata


class EnhancedDescriptionCleaner:
    """
    Advanced text cleaning utility to handle complex word concatenation, formatting issues,
    and title-based description refinement.
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
    def clean_description(description: str, title: str = None) -> str:
        """
        Comprehensive description cleaning with advanced techniques and title-based refinement.

        Args:
            description (str): Raw description text
            title (str, optional): Title of the article to help context-based cleaning

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

        # Title-based refinement
        if title:
            # Convert both title and description to lowercase
            title_words = set(title.lower().split())
            desc_words = description.lower().split()

            # Calculate the percentage of title words in the description
            title_word_overlap = sum(1 for word in desc_words if word in title_words)
            overlap_percentage = (
                (title_word_overlap / len(title_words)) if title_words else 0
            )

            # If title word overlap is low, try to extract most relevant sentences
            if overlap_percentage < 0.3:
                # Split description into sentences
                sentences = [
                    s.strip() for s in re.split(r"[.!?]", description) if s.strip()
                ]

                # Score sentences based on title word overlap
                scored_sentences = []
                for sentence in sentences:
                    sent_words = set(sentence.lower().split())
                    score = (
                        len(sent_words.intersection(title_words)) / len(sent_words)
                        if sent_words
                        else 0
                    )
                    scored_sentences.append((sentence, score))

                # Sort sentences by score and take top relevant sentences
                sorted_sentences = sorted(
                    scored_sentences, key=lambda x: x[1], reverse=True
                )

                # Take top 2-3 sentences or those with significant title overlap
                relevant_sentences = [
                    sent
                    for sent, score in sorted_sentences
                    if score > 0.2 or len(sorted_sentences) <= 3
                ]

                # Reconstruct description from most relevant sentences
                description = ". ".join(relevant_sentences) + "."

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
