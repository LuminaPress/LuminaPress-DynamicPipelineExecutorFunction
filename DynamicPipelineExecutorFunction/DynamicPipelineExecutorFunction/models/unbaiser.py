import logging
import re
from typing import List, Optional
import torch
from transformers import pipeline


class UnbiasedNewsGenerator:
    def __init__(
        self,
        biased_words: Optional[List[str]] = None,
        summarization_model: str = "facebook/bart-large-cnn",
    ):
        """
        Initialize the UnbiasedNewsGenerator with configurable bias removal and summarization.

        Args:
            biased_words: Custom list of words to remove from text
            summarization_model: Hugging Face model for text summarization
        """
        # Use a more robust default summarization model
        self.device = 0 if torch.cuda.is_available() else -1
        self.summarizer = pipeline(
            "summarization", model=summarization_model, device=self.device
        )

        # Default bias words with more nuanced selection
        self.biased_words = biased_words or [
            "unbelievable",
            "horrifying",
            "tragic",
            "incredible",
            "shocking",
            "devastating",
            "mind-blowing",
        ]

        # Configure logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def _remove_biased_language(self, text: str) -> str:
        """
        Remove emotionally charged and potentially biased words.

        Args:
            text: Input text to clean

        Returns:
            Cleaned text with biased words removed
        """
        # Use a more efficient regex for word removal
        for word in self.biased_words:
            text = re.sub(rf"\b{re.escape(word)}\b", "", text, flags=re.IGNORECASE)

        # Additional cleanup
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def generate_unbiased_news(self, news_article: str) -> str:
        """
        Generate an unbiased, summarized version of the news article.

        Args:
            news_article: Full text of the news article

        Returns:
            Cleaned and summarized article
        """
        try:
            # Remove biased language
            cleaned_article = self._remove_biased_language(news_article)

            # Generate summary with more flexible parameters
            summary = self.summarizer(
                cleaned_article,
                do_sample=True,  # Allow some creativity
                num_beams=4,  # Improve summary quality
            )

            return summary[0]["summary_text"]

        except Exception as e:
            self.logger.error(f"Error processing article: {e}")
            return news_article  # Fallback to original text if processing fails
