import logging
import datetime
from ..helper.articles.article_repository import ArticleRepository
from ..images.image_selector import ImageSelector
from ..text.text_selector import TextSelector
from ..text.text_cleaner import TextCleaner
from ..models.model_factory import ModelFactory
from tqdm import tqdm


class ArticleUpdater:
    def __init__(self, container):
        self.container = container

    def get_articles(self):
        """Fetch all articles from the database."""
        logging.info("Fetching all articles from the database.")
        query = "SELECT articles.id FROM articles"
        article_ids = [
            item["id"]
            for item in self.container.query_items(
                query, enable_cross_partition_query=True
            )
        ]
        logging.info(f"Fetched {len(article_ids)} articles.")
        return article_ids

    def fetch_article(self, article_id):
        """Fetch a single article's data from the database."""
        logging.info(f"Fetching article with ID: {article_id}")
        query = f"SELECT * FROM articles WHERE articles.id ='{article_id}'"
        article_data = list(
            self.container.query_items(query, enable_cross_partition_query=True)
        )[0]
        logging.info(f"Fetched article with ID: {article_id}")
        return article_data

    def process_article(self, article_data):
        """Process the article data to extract and update necessary fields."""
        logging.info(f"Processing article with ID: {article_data['id']}")
        tc = TextCleaner()
        ag = ArticleRepository(
            initial_titles=[article_data["title"]],
            initial_descriptions=[article_data["description"]],
            initial_imgs=[article_data["images"]],
            initial_sources=[article_data["sources"]],
        )

        # Process crowd-sourced articles if available
        for crowd_article in tqdm(
            article_data["crowd_sourced_articles"],
            desc="Processing crowd-sourced articles",
            unit="article",
        ):
            ag.get_article(crowd_article)

        # If there are crowd-sourced articles, update title, description, and images
        if len(article_data["crowd_sourced_articles"]) > 0:
            title = tc.summarize_and_clean_str(ag.get_titles(), True)
            descriptions = [
                str(item)
                for sublist in article_data["crowd_sourced_articles"]
                for item in sublist
            ]
            ts = TextSelector(title, ".".join(descriptions))
            filtered_descriptions = ts.select_relevant_text()
            description = tc.summarize_and_clean_str(ag.get_descriptions())
            imgs = ImageSelector().image_selector(
                article_data["images"], [title, description]
            )
            logging.info(
                f"Updated title and description for article ID: {article_data['id']}"
            )
        else:
            title = article_data["title"]
            description = article_data["description"]
            imgs = article_data["images"]
            logging.info(
                f"No crowd-sourced articles found for article ID: {article_data['id']}"
            )

        # Prepare the article data for update
        article_data_updated = {
            "id": article_data["id"],
            "title": title,
            "description": description,
            "Images": imgs,
            "updatedAt": datetime.datetime.now(),
            "sources": ag.get_sources()
            + article_data["crowd_sourced_articles"],  # Merging sources
            "crowd_sourced_articles": [],  # Empty out crowd-sourced articles after processing
        }

        return article_data_updated

    def update_article_in_db(self, updated_article_data):
        """Upsert the updated article data back to the database."""
        logging.info(f"Updating article with ID: {updated_article_data['id']}")
        self.container.upsert_item(updated_article_data)
        logging.info(
            f"Article with ID: {updated_article_data['id']} updated successfully."
        )

    def update_articles(self):
        """Main method to update all articles."""
        logging.info("Starting article update process.")
        article_ids = self.get_articles()

        for article_id in tqdm(article_ids, desc="Updating articles", unit="article"):
            try:
                article_data = self.fetch_article(article_id)
                updated_article_data = self.process_article(article_data)
                self.update_article_in_db(updated_article_data)
            except Exception as e:
                logging.error(f"Error updating article ID {article_id}: {e}")

        logging.info("Article update process completed.")
