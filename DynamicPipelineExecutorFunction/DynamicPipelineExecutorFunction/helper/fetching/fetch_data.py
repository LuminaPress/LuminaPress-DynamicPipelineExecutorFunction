import logging
import random
import time
from tqdm import tqdm
from bs4 import BeautifulSoup
from PIL import Image
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import os
import re


class FetchingData:
    def __init__(self, url, timeout=15, max_retries=3):
        """
        Initialize the web scraping class with enhanced configuration.

        Args:
            url (str): The URL to scrape
            timeout (int): Maximum wait time for page load and element detection
            max_retries (int): Number of times to retry scraping on failure
        """
        self.url = url
        self.content = None
        self.domain = urlparse(url).netloc
        self.driver = None
        self.timeout = timeout
        self.max_retries = max_retries
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s: %(message)s"
        )
        logging.info(f"FetchingData initialized for URL: {url}")

    def _setup_driver(self):
        """Setup chrome driver with comprehensive anti-detection settings"""
        chrome_options = Options()

        # Core anti-detection settings
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")

        # Modern anti-bot detection bypasses
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        # Specific to undetected-chromedriver for better compatibility
        return uc.Chrome(options=chrome_options)

    def _smart_delay(self, base_min=2, base_max=4, micro_min=0.1, micro_max=0.5):
        """Implement a sophisticated and less predictable delay mechanism."""
        base_delay = random.uniform(base_min, base_max)
        micro_delay = random.uniform(micro_min, micro_max)
        total_delay = base_delay + micro_delay

        logging.info(f"Smart delay: {total_delay:.2f} seconds")
        time.sleep(total_delay)

    def scroll_page(self, scroll_pause_time=1):
        """Advanced page scrolling to ensure dynamic content loading."""
        try:
            last_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )
            scroll_attempts = 0
            max_scroll_attempts = 3

            while scroll_attempts < max_scroll_attempts:
                # Smooth scrolling
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                time.sleep(scroll_pause_time)

                new_height = self.driver.execute_script(
                    "return document.body.scrollHeight"
                )
                if new_height == last_height:
                    break

                last_height = new_height
                scroll_attempts += 1

        except Exception as e:
            logging.warning(f"Scroll error: {e}")

    def get_images(self, soup):
        """
        Enhanced image extraction with comprehensive filters and Google Image search fallback.

        Args:
            soup (BeautifulSoup): Parsed HTML content

        Returns:
            list: Filtered and validated image URLs
        """

        def is_valid_google_image(url):
            """Validate Google Image search results"""
            if not url:
                return False

            # Check for common image extensions and valid URL structure
            image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg")
            url_lower = url.lower()

            return (
                url_lower.startswith(("http://", "https://"))
                and any(url_lower.endswith(ext) for ext in image_extensions)
                and "pixel" not in url_lower
                and "analytics" not in url_lower
                and "gstatic.com" not in url_lower  # Exclude Google placeholder images
                and "googleusercontent.com"
                not in url_lower  # Exclude Google-specific images
            )

        # Image extraction logic
        images = set()

        # 1. First, try to extract images from the current page
        # Find images in img tags
        for img in soup.find_all("img", src=True):
            # Try multiple attributes for image URL
            for attr in ["src", "data-src", "data-original", "data-lazy-src"]:
                url = img.get(attr)
                if url:
                    full_url = urljoin(self.url, url)
                    if is_valid_google_image(full_url):
                        images.add(full_url)

        # 2. If not enough images found, fallback to Google Image search
        if len(images) < 10:
            try:
                # Perform Google Image search using the page title as query
                title = self.get_title(soup)

                # Setup chrome driver specifically for image search
                google_driver = self._setup_driver()

                try:
                    # Construct Google Image search URL
                    search_url = f"https://www.google.com/search?q={title.replace(' ', '+')}&tbm=isch"
                    google_driver.get(search_url)

                    # Wait for initial page load
                    WebDriverWait(google_driver, self.timeout).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "div[data-ri]")
                        )
                    )

                    # Scroll to load more images
                    self.scroll_page()

                    # Extract image URLs
                    image_elements = google_driver.find_elements(
                        By.CSS_SELECTOR, "img[data-src]"
                    )

                    for element in image_elements[:10]:  # Limit to 10 additional images
                        try:
                            # Extract image URL
                            image_url = element.get_attribute("data-src")

                            # Validate and add to images set
                            if is_valid_google_image(image_url):
                                images.add(image_url)

                                # Stop if we have enough images
                                if len(images) >= 10:
                                    break
                        except Exception as e:
                            logging.warning(f"Google Image extraction error: {e}")

                except Exception as e:
                    logging.warning(f"Google Image search failed: {e}")

                finally:
                    # Always close the driver
                    google_driver.quit()

            except Exception as e:
                logging.error(f"Fallback image search error: {e}")

        return list(images)

    def get_article_content(self, soup):
        """Extract article content with better accuracy"""
        # Common article container selectors
        article_selectors = [
            "article",
            '[class*="article"]',
            '[class*="post"]',
            '[class*="content"]',
            "main",
            "#main-content",
        ]

        # Try to find the main article container
        article_container = None
        for selector in article_selectors:
            containers = soup.select(selector)
            if containers:
                # Find the container with the most paragraph tags
                article_container = max(containers, key=lambda x: len(x.find_all("p")))
                break

        if not article_container:
            article_container = soup

        # Extract paragraphs while filtering out unwanted content
        paragraphs = []
        for p in article_container.find_all("p"):
            text = p.get_text(strip=True)
            # Filter out short or irrelevant paragraphs
            if len(text) > 30 and not any(
                skip in text.lower()
                for skip in ["cookie", "subscribe", "advertisement"]
            ):
                paragraphs.append(text)

        return paragraphs

    def get_author(self, soup):
        """Enhanced author extraction"""
        author_patterns = [
            ("meta", {"name": "author"}),
            ("meta", {"property": "article:author"}),
            ("a", {"class": ["author", "byline"]}),
            ("span", {"class": ["author", "byline"]}),
            ("div", {"class": ["author", "byline"]}),
            ("p", {"class": ["author", "byline"]}),
        ]

        for tag, attrs in author_patterns:
            element = soup.find(tag, attrs)
            if element:
                if tag == "meta":
                    author = element.get("content")
                else:
                    author = element.get_text(strip=True)
                if author and len(author) > 2:
                    return author

        # If no author found, return domain name
        return self.domain

    def get_title(self, soup):
        """Enhanced title extraction"""
        # Try different methods to get the title
        title = None

        # Method 1: HTML title tag
        if soup.title:
            title = soup.title.string

        # Method 2: Open Graph title
        if not title:
            og_title = soup.find("meta", property="og:title")
            if og_title:
                title = og_title.get("content")

        # Method 3: H1 tag
        if not title:
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)

        # Method 4: Article title
        if not title:
            article_title = soup.find(
                "h1", {"class": ["title", "article-title", "entry-title"]}
            )
            if article_title:
                title = article_title.get_text(strip=True)

        return title if title else f"Article from {self.domain}"

    def scrape_website(self):
        """
        Advanced scraping method with comprehensive error handling and retry mechanism.
        """
        for attempt in range(self.max_retries):
            try:
                logging.info(f"Scraping attempt {attempt + 1} for {self.url}")

                self.driver = self._setup_driver()
                self.driver.get(self.url)

                # Wait with more flexible conditions
                WebDriverWait(self.driver, self.timeout).until(
                    lambda d: d.execute_script("return document.readyState")
                    == "complete"
                )

                # Enhanced scrolling
                self.scroll_page()
                self._smart_delay()

                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, "html.parser")

                # Extract content
                title = self.get_title(soup)
                author = self.get_author(soup)
                paragraphs = self.get_article_content(soup)
                images = self.get_images(soup)

                result = {
                    "title": title,
                    "author": author,
                    "paragraphs": paragraphs,
                    "images": images,
                    "domain": self.domain,
                    "url": self.url,
                }

                logging.info(f"Successfully scraped {self.url}")
                return result

            except (TimeoutException, WebDriverException) as e:
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                self._smart_delay(
                    base_min=3, base_max=6
                )  # Longer delay between retries
                continue

            except Exception as e:
                logging.error(f"Unhandled error scraping {self.url}: {e}")
                return {
                    "error": f"Comprehensive scraping failure: {str(e)}",
                    "domain": self.domain,
                    "url": self.url,
                }

            finally:
                if self.driver:
                    try:
                        self.driver.quit()
                    except Exception:
                        pass

        # If all attempts fail
        return {
            "error": "All scraping attempts failed",
            "domain": self.domain,
            "url": self.url,
        }
