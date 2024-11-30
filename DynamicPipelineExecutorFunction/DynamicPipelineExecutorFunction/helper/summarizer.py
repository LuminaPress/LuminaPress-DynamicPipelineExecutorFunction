from ..models.summarizers.ultra_efficient_summarizer import UltraEfficientSummarizer


def summarize_content(text: str, title: bool = False, percentage: float = 0.25) -> str:
    """Optimized wrapper function."""
    summarizer = UltraEfficientSummarizer()
    min_sentences = 1 if title else 3
    return summarizer.summarize(text, ratio=percentage, min_length=min_sentences)
