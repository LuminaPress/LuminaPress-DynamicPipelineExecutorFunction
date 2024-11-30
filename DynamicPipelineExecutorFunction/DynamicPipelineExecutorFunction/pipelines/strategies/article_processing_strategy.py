from ..new_pipeline import *
from .pipeline_strategy import *


class ArticleProcessingStrategy(PipelineStrategy):
    """Strategy for processing and inserting new articles."""

    def process(self):
        """
        Fetch and process new articles.

        Returns:
            None
        """
        processor = ArticleProcessor()
        processor.fetch_and_process_articles()
