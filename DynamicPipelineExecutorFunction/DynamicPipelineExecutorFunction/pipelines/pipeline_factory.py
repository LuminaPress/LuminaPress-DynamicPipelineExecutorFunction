import logging
from ..helper.articles.article_repository import ArticleRepository
from ..images.image_selector import ImageSelector
from ..text.text_selector import TextSelector
from ..pipelines.strategies.article_processing_strategy import ArticleProcessingStrategy
from ..pipelines.strategies.article_update_strategy import ArticleUpdateStrategy


class PipelineFactory:
    """
    Factory class for creating different types of article processing pipelines.

    This factory allows dynamic creation of different processing strategies
    based on the required pipeline type.
    """

    @staticmethod
    def create_pipeline(pipeline_type, *args, **kwargs):
        """
        Create and return a pipeline strategy based on the specified type.

        Args:
            pipeline_type (str): Type of pipeline to create
            *args: Positional arguments to pass to the strategy
            **kwargs: Keyword arguments to pass to the strategy

        Returns:
            PipelineStrategy: An instance of the requested pipeline strategy

        Raises:
            ValueError: If an invalid pipeline type is requested
        """
        logging.info(f"Creating pipeline of type: {pipeline_type}")

        if pipeline_type == "update":
            return ArticleUpdateStrategy(kwargs.get("container"))
        elif pipeline_type == "process":
            return ArticleProcessingStrategy()
        else:
            raise ValueError(f"Invalid pipeline type: {pipeline_type}")

    @staticmethod
    def execute_pipeline(pipeline_type, *args, **kwargs):
        """
        Convenience method to create and execute a pipeline in one step.

        Args:
            pipeline_type (str): Type of pipeline to create and execute
            *args: Positional arguments to pass to the strategy
            **kwargs: Keyword arguments to pass to the strategy

        Returns:
            None
        """
        try:
            pipeline = PipelineFactory.create_pipeline(pipeline_type, *args, **kwargs)
            pipeline.process()
            logging.info(f"Pipeline of type {pipeline_type} executed successfully")
        except Exception as e:
            logging.error(f"Error executing pipeline of type {pipeline_type}: {e}")
            raise
