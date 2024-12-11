import re
import torch
from typing import List, Optional, Tuple
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM


class AdvancedMarkdownGenerator:
    """
    A sophisticated markdown generation utility with advanced formatting capabilities.
    """

    def __init__(
        self, model_name: str = "google/flan-t5-base", device: Optional[str] = None
    ):
        """
        Initialize the markdown generator with advanced configuration.

        Args:
            model_name (str): Hugging Face model name
            device (Optional[str]): Compute device (cuda/cpu)
        """
        # Intelligent device selection
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        # Load model and tokenizer with enhanced configurations
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
        ).to(self.device)

        # Create pipeline with advanced settings
        self.generator = pipeline(
            "text2text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=self.device,
            max_length=1024,  # Increased max length
        )

    def _split_text(
        self, text: str, chunk_size: int = 512, overlap: int = 50
    ) -> List[str]:
        """
        Intelligent text chunking with semantic awareness.

        Args:
            text (str): Input text to chunk
            chunk_size (int): Maximum chunk size
            overlap (int): Overlap between chunks

        Returns:
            List[str]: List of text chunks
        """
        # Handle small texts
        if len(text) <= chunk_size:
            return [text]

        # Semantic chunk splitting
        chunks = []
        start = 0
        while start < len(text):
            # Extract a chunk
            chunk = text[start : start + chunk_size]

            # Try to split at sentence boundaries
            sentences = re.split(r"(?<=[.!?])\s+", chunk)

            # Combine sentences to maintain chunk size and semantic integrity
            current_chunk = []
            current_length = 0
            for sentence in sentences:
                if current_length + len(sentence) > chunk_size:
                    break
                current_chunk.append(sentence)
                current_length += len(sentence)

            chunks.append(" ".join(current_chunk))
            start += chunk_size - overlap

        return chunks

    def _clean_markdown(self, text: str) -> str:
        """
        Advanced markdown cleaning and normalization.

        Args:
            text (str): Raw markdown text

        Returns:
            str: Cleaned and formatted markdown
        """
        # Remove excessive whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)

        # Normalize list formatting
        text = re.sub(r"^(\s*[-*+])\s*", r"\1 ", text, flags=re.MULTILINE)

        # Ensure proper heading spacing
        text = re.sub(r"(^#+\s+.*)\n(?!\n)", r"\1\n\n", text, flags=re.MULTILINE)

        # Remove trailing whitespaces
        text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)

        return text.strip()

    def generate_markdown(
        self,
        text: str,
        prompt_template: Optional[str] = None,
        chunk_size: int = 512,
        overlap: int = 50,
    ) -> str:
        """
        Generate high-quality markdown with advanced processing.

        Args:
            text (str): Input text to convert
            prompt_template (Optional[str]): Custom markdown generation prompt
            chunk_size (int): Maximum chunk size
            overlap (int): Overlap between chunks

        Returns:
            str: Beautifully formatted markdown
        """
        # Default comprehensive prompt if not provided
        if prompt_template is None:
            prompt_template = (
                "Convert the following text into a professionally formatted markdown document. "
                "Use appropriate headings, create semantic lists, emphasize key points, "
                "and maintain a clear, readable structure:\n\n{}"
            )

        # Early return for empty text
        if not text:
            return ""

        # Intelligent text chunking
        text_chunks = self._split_text(text, chunk_size, overlap)

        # Prepare prompts for each chunk
        prompts = [prompt_template.format(chunk) for chunk in text_chunks]

        try:
            # Process chunks with enhanced generation parameters
            results = self.generator(
                prompts,
                max_length=1024,  # Increased max output length
                num_return_sequences=1,
                do_sample=True,  # Allow some creativity
                temperature=0.7,  # Balanced creativity and coherence
                top_k=50,  # Diverse token selection
                top_p=0.95,  # Nucleus sampling
            )

            # Combine and clean results
            combined_output = "\n\n".join(
                result["generated_text"] for result in results
            )

            return self._clean_markdown(combined_output)

        except Exception as e:
            # Fallback mechanism
            print(f"Markdown generation error: {e}")
            return text  # Return original text if generation fails
