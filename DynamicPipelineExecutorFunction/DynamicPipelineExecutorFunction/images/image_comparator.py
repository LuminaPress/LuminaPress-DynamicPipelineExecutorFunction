import logging
import torch
from transformers import BertTokenizer, BertModel, CLIPModel, CLIPProcessor
from PIL import Image
import requests
from io import BytesIO
from tqdm import tqdm
import torch.nn as nn


class ImageTextComparator:
    def __init__(self):
        # Initialize models with more robust tokenizers and models
        self.bert_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.bert_model = BertModel.from_pretrained("bert-base-uncased")
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained(
            "openai/clip-vit-base-patch32"
        )

        # Enhanced projection layer with dropout for better embedding transformation
        self.projection_layer = nn.Sequential(
            nn.Linear(768, 512), nn.ReLU(), nn.Dropout(0.1)
        )
        logging.info(
            "Initialized enhanced ImageTextComparator with BERT and CLIP models."
        )

    def _get_image_embedding(self, image_url):
        """Enhanced image embedding with better error handling and format support."""
        try:
            logging.info(f"Fetching image from URL: {image_url}")
            response = requests.get(image_url, timeout=10)
            image = Image.open(BytesIO(response.content)).convert("RGB")

            # Improved input processing
            inputs = self.clip_processor(
                images=image,
                return_tensors="pt",
                padding=True,
                do_resize=True,
                size={"shortest_edge": 224},
            )

            with torch.no_grad():
                image_embedding = self.clip_model.get_image_features(**inputs)

            logging.info("Image embedding fetched successfully.")
            return image_embedding
        except Exception as e:
            logging.error(f"Error getting image embedding: {e}")
            return None

    def _get_text_embedding(self, text):
        """Enhanced text embedding with improved tokenization and processing."""
        try:
            logging.info("Tokenizing and processing text for embedding.")
            inputs = self.bert_tokenizer(
                text, return_tensors="pt", padding=True, truncation=True, max_length=512
            )

            with torch.no_grad():
                outputs = self.bert_model(**inputs)
                pooled_output = outputs.pooler_output

            # Enhanced projection of embedding
            projected_output = self.projection_layer(pooled_output)
            logging.info("Text embedding fetched and projected.")
            return projected_output
        except Exception as e:
            logging.error(f"Error getting text embedding: {e}")
            return None

    def _normalize_embeddings(self, image_embedding, text_embedding):
        """Enhanced normalization with more robust technique."""
        logging.info("Normalizing image and text embeddings.")
        image_embedding = torch.nn.functional.normalize(image_embedding, p=2, dim=1)
        text_embedding = torch.nn.functional.normalize(text_embedding, p=2, dim=1)
        return image_embedding, text_embedding

    def compare_image_and_text(self, image_url, text, threshold=0.0):
        """Enhanced comparison with more flexible similarity calculation."""
        try:
            logging.info(
                f"Comparing image and text for similarity with threshold {threshold}."
            )
            image_embedding = self._get_image_embedding(image_url)
            text_embedding = self._get_text_embedding(text)

            if image_embedding is None or text_embedding is None:
                return False

            # Normalize the embeddings
            image_embedding, text_embedding = self._normalize_embeddings(
                image_embedding, text_embedding
            )

            # More robust similarity calculation
            similarity = torch.nn.functional.cosine_similarity(
                image_embedding, text_embedding
            )
            logging.info(f"Similarity score: {similarity.item()}")

            return similarity.item() > threshold
        except Exception as e:
            logging.error(f"Error in comparison: {e}")
            return False

    def compare_images(self, imgs_list, text, threshold=0.0):
        """Enhanced image comparison with better progress tracking."""
        matched_images = []
        logging.info(f"Comparing {len(imgs_list)} images with provided text.")

        # Using tqdm with enhanced progress tracking
        for img_url in tqdm(imgs_list, desc="Processing images", unit="image"):
            if self.compare_image_and_text(img_url, text, threshold):
                matched_images.append(img_url)

        logging.info(
            f"Found {len(matched_images)} images with similarity above threshold."
        )
        return matched_images
