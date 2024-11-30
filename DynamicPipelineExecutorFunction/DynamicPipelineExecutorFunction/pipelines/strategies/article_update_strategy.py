from ..crowdsourcing_pipeline import *
from .pipeline_strategy import *


class ArticleUpdateStrategy(PipelineStrategy):
    """Strategy for updating existing articles in the database."""

    def __init__(self, container):
        """
        Initialize the article update strategy.

        Args:
            container: Database container for querying and updating articles
        """
        self.container = container
        self.updater = ArticleUpdater(container)

    def process(self):
        """
        Process and update all articles in the database.

        Returns:
            None
        """
        self.updater.update_articles()
