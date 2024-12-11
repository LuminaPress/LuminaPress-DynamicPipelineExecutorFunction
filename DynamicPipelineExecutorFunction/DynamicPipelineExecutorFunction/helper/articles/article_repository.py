import logging
from tqdm import tqdm
from urllib.parse import urlparse
from ..fetching.fetch_data import FetchingData
from ..fetching.google_search_article_links import google_search_article_links


class ArticleRepository:
    def __init__(
        self,
        initial_titles: list = [],
        initial_imgs: list = [],
        initial_descriptions: list = [],
        initial_sources: list = [],
        initial_authors: list = [],
        min_content_threshold: int = 5,
    ) -> None:
        """
        Initialize the ArticleRepository with initial data and content retrieval thresholds.

        :param min_content_threshold: Minimum number of items before triggering additional content retrieval
        """
        self.imgs = self._clean_list(initial_imgs)
        self.descriptions = self._clean_list(initial_descriptions)
        self.titles = self._clean_list(initial_titles)
        self.sources = self._clean_list(initial_sources)
        self.authors = self._clean_authors(initial_authors)
        self.min_content_threshold = min_content_threshold
        logging.info("ArticleRepository initialized with cleaned initial data.")

    def _clean_list(self, input_list):
        """
        Clean a list by removing duplicates and empty strings.

        :param input_list: List to be cleaned
        :return: Cleaned list
        """
        # Remove empty strings and duplicates while preserving order
        cleaned = []
        seen = set()
        for item in input_list:
            # Convert to string and strip whitespace
            cleaned_item = str(item).strip()

            # Only add non-empty, unique items
            if cleaned_item and cleaned_item not in seen:
                cleaned.append(cleaned_item)
                seen.add(cleaned_item)

        return cleaned

    def _clean_authors(self, authors_list):
        """
        Clean author list by extracting domain names from URLs or cleaning text.

        :param authors_list: List of author names or URLs
        :return: Cleaned list of author names
        """
        cleaned_authors = []
        seen = set()

        for author in authors_list:
            # Convert to string and strip
            author = str(author).strip()

            # Skip empty strings
            if not author:
                continue

            # If it's a URL, extract domain
            try:
                parsed_url = urlparse(author)
                if parsed_url.netloc:
                    # Use domain name, removing www. if present
                    cleaned_author = parsed_url.netloc.replace("www.", "")
                else:
                    # Regular text author name
                    cleaned_author = author
            except:
                # Fallback to original if parsing fails
                cleaned_author = author

            # Add unique, non-empty authors
            if cleaned_author and cleaned_author not in seen:
                cleaned_authors.append(cleaned_author)
                seen.add(cleaned_author)

        return cleaned_authors

    def get_article(self, url: str):
        """Scrape an article from the given URL and store its data."""
        try:
            logging.info(f"Starting to scrape article from URL: {url}")
            fd = FetchingData(url)
            article = fd.scrape_website()

            # Extract and clean data
            images = self._clean_list(article.get("images", []))
            paragraphs = self._clean_list(article.get("paragraphs", []))
            title = str(article.get("title", "")).strip()

            # Clean and extract author
            author = (
                self._clean_authors([article.get("author", "")])[0]
                if self._clean_authors([article.get("author", "")])
                else ""
            )

            # Extend lists with cleaned data
            self.imgs.extend(images)
            if paragraphs:
                self.descriptions.extend(paragraphs)

            # Only add non-empty title
            if title:
                self.titles.append(title)

            self.sources.append(url)

            # Only add non-empty author
            if author:
                self.authors.append(author)

            logging.info(f"Scraped article: {title} from {url}")
            logging.info(
                f"Found {len(images)} images and {len(paragraphs)} paragraphs."
            )
            return True
        except Exception as e:
            logging.error(f"Error scraping article from {url}: {e}")
            return False

    def _ensure_content(self, content_list, content_type):
        """
        Ensure there's sufficient content by fetching more if needed.

        :param content_list: The list of content to check
        :param content_type: Type of content (used for logging and search)
        :return: Updated content list
        """
        if len(content_list) < self.min_content_threshold:
            logging.warning(
                f"Insufficient {content_type}. Attempting to retrieve more."
            )

            # Use titles to find more content
            search_titles = self.titles if self.titles else ["current events"]

            # Perform search to get additional links
            additional_urls = []
            for title in search_titles:
                new_urls = google_search_article_links(
                    title,
                    num_results=self.min_content_threshold - len(content_list),
                    existing_links=self.sources,
                )
                additional_urls.extend(new_urls)

                # Break if we have enough additional URLs
                if len(additional_urls) >= self.min_content_threshold - len(
                    content_list
                ):
                    break

            # Scrape additional articles
            for url in additional_urls:
                self.get_article(url)

        return content_list

    def get_titles(self):
        """Return the list of article titles, fetching more if needed."""
        self._ensure_content(self.titles, "titles")
        return self.titles

    def get_descriptions(self):
        """Return the list of article descriptions, fetching more if needed."""
        self._ensure_content(self.descriptions, "descriptions")
        return self.descriptions

    def get_images(self):
        """Return the list of article images, fetching more if needed."""
        self._ensure_content(self.imgs, "images")
        return self.imgs

    def get_sources(self):
        """Return the list of article sources (URLs), fetching more if needed."""
        self._ensure_content(self.sources, "sources")
        return self.sources

    def get_authors(self):
        """Return the list of article authors, fetching more if needed."""
        self._ensure_content(self.authors, "authors")
        return self.authors

    def scrape_multiple_articles(self, urls: list):
        """Scrape multiple articles from a list of URLs and add them to the repository."""
        logging.info(f"Starting to scrape {len(urls)} articles.")
        for url in tqdm(urls, desc="Scraping articles", unit="article"):
            self.get_article(url)
        logging.info(f"Finished scraping {len(urls)} articles.")


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
