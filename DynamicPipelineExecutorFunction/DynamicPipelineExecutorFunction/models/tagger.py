from transformers import pipeline
import numpy as np
import random
import torch

# Check if GPU is available
device = 0 if torch.cuda.is_available() else -1
# Initialize the Hugging Face zero-shot-classification pipeline
classifier = pipeline(
    "zero-shot-classification", model="facebook/bart-large-mnli", device=device
)

# Define a set of possible tags (you can expand this list)
possible_labels = [
    "Politics",
    "Economy",
    "Technology",
    "Health",
    "Science",
    "Environment",
    "Education",
    "Sports",
    "Entertainment",
    "Culture",
    "Business",
    "Lifestyle",
    "Travel",
]


# Function to generate tags
def generate_tags(title, description, num_tags=random.randint(2, len(possible_labels))):
    # Combine the title and description into a single text input
    text = title + " " + description

    # Get predictions from the zero-shot classifier
    result = classifier(text, candidate_labels=possible_labels)

    # Sort the labels by score (higher score indicates more relevance)
    sorted_labels = sorted(
        zip(result["labels"], result["scores"]), key=lambda x: x[1], reverse=True
    )

    # Get the top 'num_tags' tags
    top_tags = [label for label, score in sorted_labels[:num_tags]]

    return top_tags
