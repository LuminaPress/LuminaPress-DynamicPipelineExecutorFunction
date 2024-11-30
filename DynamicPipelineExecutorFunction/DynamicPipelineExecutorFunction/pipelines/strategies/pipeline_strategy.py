class PipelineStrategy:
    """Abstract base class for pipeline strategies."""

    def process(self, input_data):
        """
        Abstract method to be implemented by concrete strategies.

        Args:
            input_data: The data to be processed by the strategy

        Raises:
            NotImplementedError: If the method is not implemented by a subclass
        """
        raise NotImplementedError("Subclasses must implement the process method")
