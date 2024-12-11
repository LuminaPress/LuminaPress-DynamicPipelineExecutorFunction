import logging  # For logging informational and error messages
import uuid  # To generate unique IDs for articles
from datetime import datetime  # To handle timestamps
from tqdm import tqdm  # For progress bars if needed
from ...models.model_factory import (
    ModelFactory,
)  # To create a tagging model for generating tags
from ...database.db_client import CosmosDBClient  # To interact with the Cosmos DB


db_client = CosmosDBClient()


class Article_Insert:

    @staticmethod
    def article_insert(title, description, url, imgs, ag, testing={}):
        """
        Insert a new article into the Cosmos DB.

        Parameters:
        title (str): The title of the article.
        description (str): The description of the article.
        url (str): The URL of the article.
        imgs (list): List of image URLs associated with the article.
        ag (object): An object containing sources for the article (assumed to have `get_sources` method).
        """
        logging.info(f"Inserting article: {title}")
        # Prepare article data for insertion
        article_data = {
            "id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "url": [url],
            "Images": imgs,
            "publishedAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "sources": ag.get_sources(),
            "views": 0,
            "view_history": [],
            "crowd_sourced_articles": [],
            "crowd_sourced_text": [],
            "authors": ag.get_authors(),
            "tags": ModelFactory.create_model("tagger")(
                title, description
            ),  # Generate tags for the article
            "likes": 0,
            "liked_by": [],
            "comments": [],
            "testing": testing,
            "isHidden": False,
        }
        try:
            # Insert the article into Cosmos DB
            logging.info(
                f"Inserting article with ID: {article_data['id']} into Cosmos DB."
            )
            db_client.create_item(article_data)
            logging.info(f"Successfully inserted article '{title}' into the database.")
        except Exception as e:
            logging.error(f"Error inserting article '{title}' into the database: {e}")

    @staticmethod
    def update_article_insert(id, title, description, imgs, sources):
        """
        Update an existing article in Cosmos DB with new data.

        Parameters:
        id (str): The unique identifier of the article to be updated.
        title (str): The new title of the article.
        description (str): The new description of the article.
        imgs (list): List of new image URLs to be added to the article.
        sources (list): List of new sources to be added to the article.
        """
        logging.info(f"Updating article with ID: {id}")
        query = f"SELECT * FROM articles WHERE articles.id ='{id}'"

        try:
            # Query to fetch the existing article
            logging.info(f"Fetching article with ID: {id} for update.")
            items = list(db_client.query(query, enable_cross_partition_query=True))
            if not items:
                logging.warning(f"No article found with ID: {id}. Skipping update.")
                return

            document = items[0]
            # Update the article fields
            document["title"] = title
            document["description"] = description
            document["Images"].extend(imgs)  # Add new images to the existing list
            document["sources"].extend(sources)  # Add new sources to the existing list
            document["tags"] = generate_tags(title, description)
            # Upsert the updated document into Cosmos DB
            logging.info(f"Upserting updated article with ID: {id}.")
            # container.upsert_item(document)
            db_client.update_item(document.id, document.id, document)
            logging.info(f"Successfully updated article '{title}' in the database.")
        except Exception as e:
            logging.error(f"Error updating article with ID '{id}': {e}")
