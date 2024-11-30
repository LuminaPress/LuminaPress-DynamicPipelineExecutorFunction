import logging
from typing import List, Optional, Callable, Union, Tuple
from tqdm import tqdm
import numpy as np
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import re


# Download required NLTK data
try:
    nltk.download("punkt", quiet=True)
    nltk.download("stopwords", quiet=True)
except Exception as e:
    logging.warning(f"Failed to download NLTK data: {e}")


class TextSelector:
    """
    A class for selecting relevant text segments based on similarity to a reference text.
    """

    def __init__(
        self,
        true_text: str,
        test_text: str,
        model_name: str = "all-MiniLM-L6-v2",
        threshold_method: str = "kmeans",
        min_sentence_length: int = 10,
        batch_size: int = 32,
    ):
        """
        Initialize TextSelector with improved parameters and error handling.

        Args:
            true_text (str): Reference text to compare against
            test_text (str): Text to analyze and filter
            model_name (str): Name of the sentence-transformer model to use
            threshold_method (str): Method for threshold calculation ('kmeans', 'percentile', 'fixed')
            min_sentence_length (int): Minimum length of sentences to consider
            batch_size (int): Batch size for processing
        """
        self.true_text = self._preprocess_text(true_text)
        self.test_text = self._preprocess_text(test_text)
        self.min_sentence_length = min_sentence_length
        self.batch_size = batch_size
        self.threshold_method = threshold_method
        self.text_similarities: List[float] = []

        try:
            self.model = SentenceTransformer(model_name)
            logging.info(f"Initialized model: {model_name}")
        except Exception as e:
            logging.error(f"Failed to load model {model_name}: {e}")
            raise

        logging.info(
            f"Initialized TextSelector with true_text length: {len(self.true_text)} "
            f"and test_text length: {len(self.test_text)}"
        )

    @staticmethod
    def _preprocess_text(text: str) -> str:
        """
        Preprocess text with improved cleaning and normalization.

        Args:
            text (str): Input text to preprocess

        Returns:
            str: Cleaned and normalized text
        """
        if not isinstance(text, str):
            text = str(text)

        # Remove special characters and normalize spaces
        text = re.sub(
            r"(?<=\w)\.\.\.(?=\w)", " ", text
        )  # Remove ellipsis between words
        text = re.sub(r"\s+", " ", text)  # Normalize whitespace
        text = re.sub(r"[^\w\s.,!?-]", "", text)  # Remove special characters

        return text.strip()

    def _split_test_text(self) -> List[str]:
        """
        Split test text into sentences with improved sentence boundary detection.

        Returns:
            List[str]: List of preprocessed sentences
        """
        logging.info("Splitting test text into sentences.")

        try:
            # Use NLTK's sentence tokenizer
            sentences = sent_tokenize(self.test_text)

            # Filter sentences based on length and content
            filtered_sentences = [
                sent.strip()
                for sent in sentences
                if len(sent.strip()) >= self.min_sentence_length
                and any(c.isalnum() for c in sent)
            ]

            logging.debug(
                f"Split test text into {len(filtered_sentences)} valid sentences."
            )
            return filtered_sentences

        except Exception as e:
            logging.error(f"Error in sentence splitting: {e}")
            return [self.test_text]  # Fallback to returning the entire text

    def _calculate_similarities_batch(self, sentences: List[str]) -> List[float]:
        """
        Calculate similarities using batched processing for better performance.

        Args:
            sentences (List[str]): List of sentences to process

        Returns:
            List[float]: List of similarity scores
        """
        try:
            # Encode true text once
            true_embedding = self.model.encode([self.true_text])[0]

            similarities = []
            for i in tqdm(
                range(0, len(sentences), self.batch_size), desc="Processing batches"
            ):
                batch = sentences[i : i + self.batch_size]
                batch_embeddings = self.model.encode(batch)

                # Calculate cosine similarity for the batch
                batch_similarities = [
                    np.dot(true_embedding, sent_emb)
                    / (np.linalg.norm(true_embedding) * np.linalg.norm(sent_emb))
                    for sent_emb in batch_embeddings
                ]
                similarities.extend(batch_similarities)

            return similarities

        except Exception as e:
            logging.error(f"Error in similarity calculation: {e}")
            return [0.0] * len(sentences)

    def _calculate_threshold(self, similarities: List[float]) -> float:
        """
        Calculate threshold using the specified method.

        Args:
            similarities (List[float]): List of similarity scores

        Returns:
            float: Calculated threshold value
        """
        if len(similarities) == 0:
            return 0.0

        if self.threshold_method == "kmeans":
            # Use KMeans to find natural threshold
            kmeans = KMeans(n_clusters=2, random_state=42)
            data = np.array(similarities).reshape(-1, 1)
            kmeans.fit(data)
            threshold = np.mean(kmeans.cluster_centers_)

        elif self.threshold_method == "percentile":
            # Use percentile-based threshold
            threshold = np.percentile(similarities, 75)

        else:  # fixed threshold
            threshold = 0.5

        logging.info(
            f"Calculated threshold: {threshold:.3f} using method: {self.threshold_method}"
        )
        return threshold

    def select_relevant_text(
        self, return_scores: bool = False
    ) -> Union[List[str], Tuple[List[str], List[float]]]:
        """
        Select relevant sentences from test text based on similarity to true text.

        Args:
            return_scores (bool): Whether to return similarity scores along with sentences

        Returns:
            Union[List[str], Tuple[List[str], List[float]]]: Selected sentences and optionally their scores
        """
        logging.info("Starting text selection process.")

        try:
            # Split and preprocess text
            sentences = self._split_test_text()
            if not sentences:
                logging.warning("No valid sentences found in test text.")
                return ([], []) if return_scores else []

            # Calculate similarities
            self.text_similarities = self._calculate_similarities_batch(sentences)

            # Calculate threshold and filter sentences
            threshold = self._calculate_threshold(self.text_similarities)
            selected_pairs = [
                (sent, score)
                for sent, score in zip(sentences, self.text_similarities)
                if score > threshold
            ]

            # Sort by similarity score in descending order
            selected_pairs.sort(key=lambda x: x[1], reverse=True)

            # Separate sentences and scores
            selected_sentences, selected_scores = (
                zip(*selected_pairs) if selected_pairs else ([], [])
            )

            logging.info(f"Selected {len(selected_sentences)} relevant sentences.")

            return (
                (list(selected_sentences), list(selected_scores))
                if return_scores
                else list(selected_sentences)
            )

        except Exception as e:
            logging.error(f"Error in text selection process: {e}")
            return ([], []) if return_scores else []

    def get_summary_statistics(self) -> dict:
        """
        Get summary statistics of the text selection process.

        Returns:
            dict: Dictionary containing summary statistics
        """
        return {
            "total_sentences": len(self.text_similarities),
            "mean_similarity": (
                np.mean(self.text_similarities) if self.text_similarities else 0
            ),
            "max_similarity": (
                max(self.text_similarities) if self.text_similarities else 0
            ),
            "min_similarity": (
                min(self.text_similarities) if self.text_similarities else 0
            ),
            "std_similarity": (
                np.std(self.text_similarities) if self.text_similarities else 0
            ),
        }
