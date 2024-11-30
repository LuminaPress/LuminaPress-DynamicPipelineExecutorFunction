import re
import logging
from tqdm import tqdm


class TextCleaner:
    def __init__(self, splitter: str = "."):
        self.splitter = splitter
        logging.info(f"TextCleaner initialized with splitter: '{self.splitter}'")

    def summarize_and_clean_str(self, text_collection: list, title: bool = False):
        """
        Summarizes and cleans a collection of text by joining them and applying cleaning functions.
        Args:
            text_collection (list): A list of strings to be processed.

        Returns:
            str: Cleaned and summarized text.
        """
        from ..helper.summarizer import (
            summarize_content,
        )

        logging.info(
            f"Starting summary and cleaning of text collection of length {len(text_collection)}."
        )
        summarized_text = summarize_content(".".join(text_collection), title)
        cleaned_text = self.clean_str(summarized_text).strip()
        logging.info(
            f"Summary and cleaning completed. Cleaned text length: {len(cleaned_text)}."
        )
        return cleaned_text

    def clean_str(self, text: str) -> str:
        # Fail-safe to handle non-string inputs
        if not isinstance(text, str):
            try:
                text = str(text)
            except:
                return ""

        # Comprehensive cleaning pipeline
        def clean_pipeline(input_text):
            # Logging stage (if logging is set up)
            try:
                logging.debug(f"Cleaning text: {input_text[:100]}...")
            except:
                pass

            # Extensive cleanup stages
            stages = [
                # Remove HTML-like tags globally
                lambda t: re.sub(r"<[^>]+>", "", t),
                # Remove URLs of all types
                lambda t: re.sub(
                    r"https?://\S+|www\.\S+|\S+\.(com|org|net|edu)\S*", "", t
                ),
                # Remove social media and source attributions
                lambda t: re.sub(
                    r"\s*-\s*(ABC|NBC|Fox|CNN|MSNBC|News|Twitter|X|Facebook|Reddit|Instagram|Yahoo|Reuters).*$",
                    "",
                    t,
                    flags=re.IGNORECASE,
                ),
                # Remove prefixes like "Page Unavailable", "BREAKING:", etc.
                lambda t: re.sub(
                    r"^(Page\s*Unavailable\s*-?|BREAKING\s*:?|ALERT\s*:?)",
                    "",
                    t,
                    flags=re.IGNORECASE,
                ),
                # Remove quotes (single and double)
                lambda t: t.replace('"', "").replace("'", ""),
                # Remove ellipses and excessive punctuation
                lambda t: re.sub(r"\.{3,}", "", t),
                # Remove repetitive "No Title" type entries
                lambda t: re.sub(r"^(No\s*Title\s*){1,}", "", t, flags=re.IGNORECASE),
                # Remove common repetitive metadata phrases
                lambda t: re.sub(
                    r"\s*(My\s*first\s*bet|Game\s*Recap|Morning\s*Break|What\s*We\s*Learned|Live\s*updates\s*and\s*reaction).*$",
                    "",
                    t,
                    flags=re.IGNORECASE,
                ),
                # Remove common sports-related metadata
                lambda t: re.sub(
                    r"\s*-\s*(ESPN|The\s*Athletic|X).*$", "", t, flags=re.IGNORECASE
                ),
                # Remove corporate and brand-related metadata
                lambda t: re.sub(
                    r"\s*is part of the\s*.*\s*family of brands",
                    "",
                    t,
                    flags=re.IGNORECASE,
                ),
                # Remove additional corporate/publication phrases
                lambda t: re.sub(
                    r"\s*-\s*(By\s*[A-Za-z]+).*$", "", t, flags=re.IGNORECASE
                ),
                # Normalize whitespace
                lambda t: re.sub(r"\s+", " ", t),
                # Remove trailing website domains
                lambda t: re.sub(
                    r"\s*\b(go\.com|news\.com|online)\s*$", "", t, flags=re.IGNORECASE
                ),
                # Remove common metadata markers
                lambda t: re.sub(
                    r"\s*originally\s*appeared\s*on.*$", "", t, flags=re.IGNORECASE
                ),
                # Trim leading/trailing whitespace
                lambda t: t.strip(),
            ]

            # Apply all cleaning stages
            for stage in stages:
                input_text = stage(input_text)

            return input_text

        # Main cleaning process with error handling
        try:
            cleaned_text = clean_pipeline(text)

            # Final safety checks
            cleaned_text = cleaned_text.strip()

            # Optional: Log cleaning results
            try:
                logging.debug(f"Cleaned text: {cleaned_text[:100]}...")
            except:
                pass

            return cleaned_text

        except Exception as e:
            # Fallback to minimal cleaning if something goes wrong
            try:
                logging.error(f"Text cleaning failed: {e}")
            except:
                pass

            return text.strip()

    def clean_batch(self, text_collection: list):
        """
        Cleans a batch of text strings and returns the cleaned collection.

        Args:
            text_collection (list): A list of strings to be cleaned.

        Returns:
            list: A list of cleaned strings.
        """
        cleaned_texts = []
        logging.info(f"Starting batch cleaning of {len(text_collection)} texts.")

        # Iterate through the collection with tqdm for progress bar
        for text in tqdm(text_collection, desc="Cleaning Texts", ncols=100):
            cleaned_text = self.clean_str(text)
            cleaned_texts.append(cleaned_text)

        logging.info(f"Batch cleaning completed. Cleaned {len(cleaned_texts)} texts.")
        return cleaned_texts
