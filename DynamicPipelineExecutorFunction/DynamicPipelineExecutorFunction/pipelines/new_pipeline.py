import logging
import threading
from ..helper.articles.article_repository import ArticleRepository
from ..images.image_selector import ImageSelector
from ..text.text_selector import TextSelector
from ..helper import *
from ..models.model_factory import ModelFactory
from tqdm import tqdm
from datetime import datetime
from ..models.unbaiser import UnbiasedNewsGenerator
from ..helper.fetching.fetch_news_data import *
from ..text.text_cleaner import TextCleaner
from ..text.generators.title_generator import ElegantTitleGenerator
from ..helper.articles.article_insert import Article_Insert
from ..models.summarizers.flow_oriented_description_summarizer import (
    FlowOrientedDescriptionSummarizer,
)
from ..helper.fetching.google_search_article_links import google_search_article_links


class ArticleProcessor:
    def __init__(self):
        self.threads = []
        self.UnbiasedNewsGenerator = UnbiasedNewsGenerator()
        logging.info("ArticleProcessor initialized.")

    def fetch_and_process_articles(self):
        """Fetch new articles and process them in parallel using threading."""
        logging.info("Fetching new articles...")
        articles = fetch_news_data()
        logging.info(f"Fetched {len(articles)} articles.")

        # Iterate through articles with a progress bar
        for article in tqdm(articles, desc="Processing articles", unit="article"):
            self.process_article(article)

        logging.info(f"Timer trigger function completed at: {datetime.utcnow()}")

    def process_article(self, article):
        """Process a single article: summarize, fetch similar articles, and insert it into the database."""
        print(article)
        tc = TextCleaner()
        title = article.get("title", "")
        url = article.get("url", "No URL")
        logging.info(f"Started processing article: {title} ({url})")
        ag = ArticleRepository()
        ag.get_article(url)
        # Adding similar articles
        logging.info(f"Fetching similar articles for: {title}")
        ag = self.add_similar_articles(ag, title)
        # Summarize title and description
        logging.info(f"Summarizing content for: {title}")
        # title_generator = ElegantTitleGenerator()
        # title = self.UnbiasedNewsGenerator.generate_unbiased_news(
        #     title_generator.generate_elegant_title(ag.get_titles(), max_length=75)
        # )
        title = title
        # Description generation
        description_summarizer = FlowOrientedDescriptionSummarizer()
        description = self.UnbiasedNewsGenerator.generate_unbiased_news(
            description_summarizer.generate_flowing_description(
                ag.get_descriptions(), max_sentences=5
            )
        )

        # Select relevant images
        logging.info(f"Selecting images for article: {title}")
        imgs = ImageSelector().image_selector(ag.get_images(), [title, description])
        # Insert the article into the database
        logging.info(f"Inserting article into database: {title}")
        Article_Insert.article_insert(
            title,
            description,
            url,
            imgs,
            ag,
        )
        logging.info(f"Successfully added article: {title}")

    def add_similar_articles(self, ag, title):
        """Find and add similar articles by performing a Google search."""
        logging.info(f"Searching for similar articles to: {title}")
        similar_articles = google_search_article_links(title)

        # Iterate through similar articles with a progress bar
        for similar_article in tqdm(
            similar_articles,
            desc=f"Processing similar articles for {title}",
            unit="similar article",
        ):
            ag.get_article(similar_article)
        logging.info(f"Finished processing similar articles for: {title}")
        return ag

    def wait_for_threads(self):
        """Wait for all threads to finish."""
        logging.info(f"Waiting for {len(self.threads)} threads to complete.")
        for thread in self.threads:
            # Ensure we do not try to join the current thread
            if thread != threading.current_thread():
                thread.join()
        self.threads = []  # Reset the thread list after processing
        logging.info("All threads completed.")
