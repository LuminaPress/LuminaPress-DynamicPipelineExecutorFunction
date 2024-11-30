from .summarizers.ultra_efficient_summarizer import UltraEfficientSummarizer
from .summarizers.flow_oriented_description_summarizer import (
    FlowOrientedDescriptionSummarizer,
)
from .summarizers.advanced_summarizer import advanced_summarizer
from .tagger import generate_tags
from .markdowner import text_to_markdown
from .unbaiser import UnbiasedNewsGenerator


class ModelFactory:
    """
    Factory class to create instances of different models.
    """

    @staticmethod
    def create_model(model_type: str, **kwargs):
        """
        Create and return a model instance based on the model type.

        Args:
            model_type (str): Type of the model (e.g., 'summarizer', 'tagger').

        Returns:
            object: Instance of the requested model class.
        """
        if model_type == "ultra_efficient_summarizer":
            from .summarizers.ultra_efficient_summarizer import UltraEfficientSummarizer

            return UltraEfficientSummarizer(**kwargs)
        elif model_type == "flow_oriented_description_summarizer":
            from .summarizers.flow_oriented_description_summarizer import (
                FlowOrientedDescriptionSummarizer,
            )

            return FlowOrientedDescriptionSummarizer(**kwargs)
        elif model_type == "advanced_summarizer":
            from .summarizers.advanced_summarizer import (
                advanced_summarizer,
            )

            return advanced_summarizer
        elif model_type == "tagger":
            from .tagger import generate_tags

            return generate_tags
        elif model_type == "markdowner":
            from .markdowner import text_to_markdown

            return text_to_markdown
        elif model_type == "unbaiser":
            from .unbaiser import UnbiasedNewsGenerator

            return UnbiasedNewsGenerator(**kwargs)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
