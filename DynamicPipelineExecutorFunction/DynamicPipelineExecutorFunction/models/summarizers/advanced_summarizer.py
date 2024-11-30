import logging
from tqdm import tqdm
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.nlp.tokenizers import Tokenizer
from sumy.utils import get_stop_words


# Optimized function to summarize text
def advanced_summarizer(text, title=False, percentage=0.125):
    """
    Summarize the provided text using the TextRank algorithm.

    Args:
        text (str): The text to summarize.
        title (bool): Whether the summary is for a title (defaults to False).
        percentage (float): Percentage of the content to be included in the summary (defaults to 0.25).

    Returns:
        str: The summarized text.
    """

    logging.info("Starting summarization process.")
    if not text.strip():
        logging.warning("Empty text provided for summarization.")
        return ""
    # Tokenize and parse the text
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    logging.debug(f"Text length: {len(text)} characters.")
    # Use TextRank summarizer
    summarizer = TextRankSummarizer()
    summarizer.stop_words = get_stop_words(
        "english"
    )  # Add stop words for better performance
    # Calculate the number of sentences to summarize
    sentence_count = len(list(parser.document.sentences))
    num_sentences = max(1, int(sentence_count * percentage)) if not title else 1
    logging.debug(
        f"Summarizing into {num_sentences} sentences (out of {sentence_count})."
    )
    # Generate the summary
    summary = summarizer(parser.document, num_sentences)
    summarized_text = " ".join(str(sentence) for sentence in summary)
    logging.info("Summarization completed.")
    return summarized_text
