from typing import List
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ...text.generators.description_generator import EnhancedDescriptionCleaner


# Updated FlowOrientedDescriptionSummarizer to use the new cleaner
class FlowOrientedDescriptionSummarizer:
    def __init__(self):
        self.description_cleaner = EnhancedDescriptionCleaner()

    def _extract_flowing_sentences(
        self, descriptions: List[str], max_sentences: int
    ) -> str:
        """
        Extract semantically connected sentences.

        Args:
            descriptions: Cleaned descriptions
            max_sentences: Maximum sentences to include

        Returns:
            Flowing description text
        """
        # Tokenize all descriptions
        all_sentences = []
        for desc in descriptions:
            all_sentences.extend(sent_tokenize(desc))

        # Use TF-IDF to rank sentences
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(all_sentences)

        # Calculate sentence centrality
        similarity_matrix = cosine_similarity(tfidf_matrix)
        centrality_scores = similarity_matrix.sum(axis=1)

        # Select top sentences maintaining flow
        top_sentence_indices = centrality_scores.argsort()[-max_sentences:][::-1]
        flowing_sentences = [all_sentences[idx] for idx in top_sentence_indices]

        return " ".join(flowing_sentences)

    def generate_flowing_description(
        self, descriptions: List[str], max_sentences: int = 3
    ) -> str:
        """
        Create a flowing, coherent description with enhanced cleaning.

        Args:
            descriptions: List of raw descriptions
            max_sentences: Maximum number of sentences

        Returns:
            Coherent, flowing description
        """
        # Clean and filter descriptions
        cleaned_descriptions = [
            self.description_cleaner.clean_description(desc) for desc in descriptions
        ]

        # Remove near-duplicates
        unique_descriptions = self.description_cleaner.remove_near_duplicates(
            cleaned_descriptions
        )

        # Extract key sentences (existing method remains the same)
        flowing_description = self._extract_flowing_sentences(
            unique_descriptions, max_sentences
        )

        return flowing_description

    # Rest of the class remains the same as in previous implementation
