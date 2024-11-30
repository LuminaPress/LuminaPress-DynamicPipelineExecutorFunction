import logging
from sentence_transformers import SentenceTransformer, util


class TextComparator:
    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

    def __init__(self, text1: str, text2: str, threshold: float = 0.0):
        self.text1 = self._str_converter(text1)
        self.text2 = self._str_converter(text2)
        self.threshold = threshold
        self.encoding1 = self._get_encoding(self.text1)
        self.encoding2 = self._get_encoding(self.text2)

    @staticmethod
    def _str_converter(text) -> str:
        """Convert the input to a string if it's not already a string."""
        if not isinstance(text, str):
            logging.debug(f"Converting input of type {type(text)} to string.")
            text = str(text)
        return text

    @staticmethod
    def _get_encoding(text: str):
        """Get the embeddings of the text using the SentenceTransformer model."""
        logging.debug(
            f"Encoding text: {text[:30]}..."
        )  # Log the first 30 characters for brevity
        return TextComparator.model.encode(text, convert_to_tensor=True)

    def compare(self) -> dict:
        """Compares the two texts and returns the cosine similarity."""
        similarity_score = util.pytorch_cos_sim(self.encoding1, self.encoding2).item()
        return {"similarity_score": similarity_score}

    def is_match(self, score_out=False) -> bool:
        """Checks if the similarity score is above the threshold."""
        score = self.compare()["similarity_score"]
        match = score >= self.threshold
        if score_out:
            return score, match
        return match
