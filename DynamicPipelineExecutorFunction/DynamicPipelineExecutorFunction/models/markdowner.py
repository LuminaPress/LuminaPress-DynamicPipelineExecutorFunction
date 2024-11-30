from transformers import pipeline
import torch
from typing import List
import re

# Initialize device globally - this only needs to be done once
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Initialize the model globally - avoid recreating it multiple times
MODEL_NAME = "google/flan-t5-small"
generator = pipeline(
    "text2text-generation",
    model=MODEL_NAME,
    device=DEVICE,
    model_kwargs={
        "torch_dtype": torch.float16
    },  # Use half precision for better memory efficiency
)


def split_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Split text into chunks efficiently using list comprehension."""
    if len(text) <= chunk_size:
        return [text]

    # Calculate positions where chunks should start
    positions = range(0, len(text), chunk_size - overlap)

    # Create chunks using list comprehension
    return [text[pos : pos + chunk_size] for pos in positions]


def clean_output(text: str) -> str:
    """Clean and normalize markdown output."""
    # Remove redundant newlines and spaces
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def text_to_markdown(
    text: str,
    prompt_template: str = "Format the following text into Markdown with headings and lists:\n\n{}",
    chunk_size: int = 512,
    overlap: int = 50,
) -> str:
    """
    Convert text to markdown format more efficiently.

    Args:
        text (str): Input text to convert
        prompt_template (str): Template for formatting prompt
        chunk_size (int): Maximum size of each text chunk
        overlap (int): Number of characters to overlap between chunks

    Returns:
        str: Formatted markdown text
    """
    # Early return for empty text
    if not text:
        return ""

    # Process text in batches
    text_chunks = split_text(text, chunk_size, overlap)

    # Prepare all prompts at once
    prompts = [prompt_template.format(chunk) for chunk in text_chunks]

    # Process all chunks in one batch
    results = generator(
        prompts,
        max_length=chunk_size,
        batch_size=4,  # Adjust based on your GPU memory
        num_return_sequences=1,
        do_sample=False,  # Deterministic output for better consistency
    )

    # Combine results efficiently
    combined_output = "\n\n".join(result["generated_text"] for result in results)

    # Clean and return the final output
    return clean_output(combined_output)
