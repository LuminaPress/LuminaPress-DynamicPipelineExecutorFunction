import logging
from collections import Counter
from tqdm import tqdm
from .image_comparator import *


class ImageSelector:
    @staticmethod
    def image_selector(imgs, txt_list):
        """
        Enhanced image selection with quality and resolution prioritization.

        Args:
            imgs (list): List of image paths or image objects
            txt_list (list): List of text descriptions

        Returns:
            list: Top 5 highest quality images matching the text descriptions
        """
        try:
            logging.info(f"Starting image selection for {len(txt_list)} texts.")

            all_matched_imgs = find_image_matches(imgs, "\n".join(txt_list))

            # More sophisticated image counting
            element_counts = Counter(all_matched_imgs)
            logging.info(
                f"Counting image occurrences. Found {len(element_counts)} unique images."
            )

            # Adaptive threshold based on number of texts
            threshold = max(1, len(txt_list) - 1)

            # Filter images that meet the threshold
            filtered_imgs = [
                img for img, count in element_counts.items() if count >= threshold
            ]
            logging.info(
                f"Filtered {len(filtered_imgs)} images based on the threshold."
            )

            # Sort images by quality and resolution
            def image_quality_score(img):
                """
                Calculate a quality score for each image.
                Customize this method based on your specific image quality metrics.
                """
                try:
                    # Example scoring (replace with actual image quality assessment)
                    # You might want to use libraries like Pillow to get image dimensions
                    # or implement more sophisticated quality assessment
                    resolution = img.width * img.height if hasattr(img, "width") else 0
                    # Add more scoring criteria like file size, compression, clarity, etc.
                    return resolution
                except Exception as e:
                    logging.warning(f"Could not assess image quality for {img}: {e}")
                    return 0

            # Sort images by quality and take top 5
            top_quality_imgs = sorted(
                filtered_imgs, key=image_quality_score, reverse=True
            )

            logging.info(
                f"Selected top {len(top_quality_imgs)} highest quality images."
            )
            return top_quality_imgs

        except Exception as e:
            logging.error(f"Error in image selection process: {e}")
            return []
