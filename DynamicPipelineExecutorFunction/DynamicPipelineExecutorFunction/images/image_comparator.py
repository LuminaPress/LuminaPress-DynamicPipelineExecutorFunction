import logging
import torch
from transformers import BertTokenizer, BertModel, CLIPModel, CLIPProcessor
from PIL import Image
import requests
from io import BytesIO
import torch.nn as nn
import re


class ImageRelevanceFinder:
    def __init__(self, confidence_threshold=0.65, high_confidence_threshold=0.75):
        # Initialize models with advanced pre-trained weights
        self.bert_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.bert_model = BertModel.from_pretrained("bert-base-uncased")
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained(
            "openai/clip-vit-base-patch32"
        )

        # Enhanced embedding projection layer
        self.projection_layer = nn.Sequential(
            nn.Linear(768, 512), nn.ReLU(), nn.Dropout(0.1)
        )

        # Confidence thresholds
        self.confidence_threshold = confidence_threshold
        self.high_confidence_threshold = high_confidence_threshold

    def _validate_url(self, url):
        """Validate URL structure."""
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        return bool(url_pattern.match(url))

    def _get_text_embedding(self, text):
        """Generate text embedding using BERT."""
        try:
            inputs = self.bert_tokenizer(
                text, return_tensors="pt", padding=True, truncation=True, max_length=512
            )

            with torch.no_grad():
                outputs = self.bert_model(**inputs)
                pooled_output = outputs.pooler_output

            return self.projection_layer(pooled_output)
        except Exception as e:
            logging.error(f"Text embedding error: {e}")
            return None

    def _get_image_embedding(self, image_url):
        """Generate image embedding using CLIP."""
        try:
            response = requests.get(image_url, timeout=10)
            image = Image.open(BytesIO(response.content)).convert("RGB")

            inputs = self.clip_processor(
                images=image,
                return_tensors="pt",
                padding=True,
                do_resize=True,
                size={"shortest_edge": 224},
            )

            with torch.no_grad():
                return self.clip_model.get_image_features(**inputs)
        except Exception as e:
            logging.error(f"Image embedding error for {image_url}: {e}")
            return None

    def find_relevant_images(self, image_urls, description, title=None, top_k=5):
        """
        Find most relevant images based on description and optional title.

        Args:
        - image_urls (list): List of image URLs to check
        - description (str): Detailed description for context
        - title (str, optional): Additional title context
        - top_k (int): Number of top relevant images to return

        Returns:
        - list: Most relevant image URLs with confidence scores
        """
        # Validate inputs
        if not image_urls or not description:
            return []

        # Prepare text embeddings
        description_embedding = self._get_text_embedding(description)
        title_embedding = self._get_text_embedding(title) if title else None

        # If description embedding fails, return empty
        if description_embedding is None:
            return []

        # Results tracking
        image_relevance = []

        # Process each image
        for image_url in image_urls:
            # Skip invalid URLs
            if not self._validate_url(image_url):
                continue

            try:
                # Get image embedding
                image_embedding = self._get_image_embedding(image_url)
                if image_embedding is None:
                    continue

                # Normalize embeddings
                description_embedding_norm = torch.nn.functional.normalize(
                    description_embedding, p=2, dim=1
                )
                image_embedding_norm = torch.nn.functional.normalize(
                    image_embedding, p=2, dim=1
                )

                # Calculate similarity
                similarity = torch.nn.functional.cosine_similarity(
                    description_embedding_norm, image_embedding_norm
                ).item()

                # Optional title boost
                title_boost = 0
                if title and title_embedding is not None:
                    title_embedding_norm = torch.nn.functional.normalize(
                        title_embedding, p=2, dim=1
                    )
                    title_similarity = torch.nn.functional.cosine_similarity(
                        title_embedding_norm, image_embedding_norm
                    ).item()
                    title_boost = title_similarity * 0.2

                # Total confidence score
                total_confidence = similarity + title_boost

                # Store results for confident matches
                if total_confidence > self.confidence_threshold:
                    image_relevance.append(
                        {"url": image_url, "confidence": total_confidence}
                    )

            except Exception as e:
                logging.error(f"Error processing {image_url}: {e}")

        # Sort and return top K most relevant images
        return sorted(image_relevance, key=lambda x: x["confidence"], reverse=True)[
            :top_k
        ]


def find_image_matches(image_urls, description, title=None, top_k=5):
    """
    Simplified wrapper to find most relevant images

    Args:
    - image_urls (list): List of image URLs
    - description (str): Detailed context description
    - title (str, optional): Optional title for extra context
    - top_k (int): Number of top images to return

    Returns:
    - list: Most relevant image URLs with confidence scores
    """
    finder = ImageRelevanceFinder()
    return finder.find_relevant_images(image_urls, description, title, top_k)
