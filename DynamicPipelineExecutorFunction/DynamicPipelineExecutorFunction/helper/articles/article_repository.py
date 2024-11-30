import logging  # For logging informational and error messages
from tqdm import tqdm  # For progress bars when scraping multiple articles
from ..fetching.fetch_data import FetchingData  # To fetch and scrape article data
from datetime import datetime  # (Optional) If timestamps are required later


class ArticleRepository:
    def __init__(
        self,
        initial_titles: list = [],
        initial_imgs: list = [],
        initial_descriptions: list = [],
        initial_sources: list = [],
        initial_authors: list = [],
    ) -> None:
        """Initialize the ArticleRepository with initial data."""
        self.imgs = initial_imgs
        self.descriptions = initial_descriptions
        self.titles = initial_titles
        self.sources = initial_sources
        self.authors = initial_authors
        logging.info("ArticleRepository initialized with initial data.")

    def get_article(self, url: str):
        """Scrape an article from the given URL and store its data."""
        try:
            logging.info(f"Starting to scrape article from URL: {url}")
            fd = FetchingData(url)
            article = fd.scrape_website()

            # Extract data and add to respective lists
            images = article.get("images", [])
            paragraphs = article.get("paragraphs", [])
            title = article.get("title", "No Title")

            self.imgs.extend(images)
            self.descriptions.extend(paragraphs)
            self.titles.append(title)
            self.sources.append(url)
            self.authors.append(article.get("author"))
            logging.info(f"Scraped article: {title} from {url}")
            logging.info(
                f"Found {len(images)} images and {len(paragraphs)} paragraphs."
            )
            return True
        except Exception as e:
            logging.error(f"Error scraping article from {url}: {e}")
            return False

    def get_titles(self):
        """Return the list of article titles."""
        return self.titles

    def get_descriptions(self):
        """Return the list of article descriptions."""
        return self.descriptions

    def get_images(self):
        """Return the list of article images."""
        return self.imgs

    def get_sources(self):
        """Return the list of article sources (URLs)."""
        return self.sources

    def scrape_multiple_articles(self, urls: list):
        """Scrape multiple articles from a list of URLs and add them to the repository."""
        logging.info(f"Starting to scrape {len(urls)} articles.")
        for url in tqdm(urls, desc="Scraping articles", unit="article"):
            self.get_article(url)
        logging.info(f"Finished scraping {len(urls)} articles.")

    def get_authors(self):
        return self.authors


# from serpapi import GoogleSearch

# def get_google_images(query, api_key, num_results=10):
#     params = {
#         "q": query,
#         "tbm": "isch",  # Search type: images
#         "ijn": "0",  # First page of results
#         "api_key": api_key,
#     }

#     search = GoogleSearch(params)
#     results = search.get_dict()

#     # Extract image links from the response
#     image_results = results.get("images_results", [])
#     images = [img.get("original") for img in image_results[:num_results]]

#     return images

# # Replace with your SerpAPI key
# API_KEY = "your_serpapi_key_here"
# query_term = "sunset landscape"

# # Get the top 10 image URLs
# image_urls = get_google_images(query_term, API_KEY)

# print("Top 10 Google Image URLs:")
# for idx, url in enumerate(image_urls, start=1):
#     print(f"{idx}: {url}")
