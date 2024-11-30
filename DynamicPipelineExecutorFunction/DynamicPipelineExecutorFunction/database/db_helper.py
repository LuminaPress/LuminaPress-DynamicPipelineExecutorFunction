import logging  # For logging messages
from tqdm import tqdm  # For progress tracking
from azure.cosmos import CosmosClient, PartitionKey  # For interacting with Cosmos DB
from ..core import *  # Assuming the core module provides required utilities, e.g., `client`


class CosmosDBHelper:

    @staticmethod
    def create_database_if_not_exists(database_name="articles"):
        """
        Checks if the database exists, and if not, creates it.

        Parameters:
        database_name (str): The name of the database to check or create.
        """
        database = client.get_database_client("articles")
        container = database.get_container_client("articles")
        logging.info(
            f"Checking if database '{database_name}' exists or needs to be created."
        )
        try:
            database = client.create_database_if_not_exists(id=database_name)
            logging.info(f"Database '{database_name}' is ready (checked or created).")
            return database
        except Exception as e:
            logging.error(f"Error checking or creating database '{database_name}': {e}")
            return None

    @staticmethod
    def create_container_if_not_exists(
        database_name="articles", container_name="articles"
    ):
        """
        Checks if the container exists in the specified database, and if not, creates it.

        Parameters:
        database (str): The name of the database to check or create the container in.
        container_name (str): The name of the container to check or create.
        """
        database = client.get_database_client("articles")
        container = database.get_container_client("articles")
        logging.info(
            f"Checking if container '{container_name}' exists or needs to be created in database '{database}'."
        )
        container = database.create_container_if_not_exists(
            id=container_name,
            partition_key=PartitionKey(path="/id"),  # Change partition key if needed
            offer_throughput=400,  # Adjust throughput as needed
        )
        logging.info(f"Container '{container_name}' is ready (checked or created).")
        return container

    @staticmethod
    def clear_container(container_name="articles"):
        """
        Clears all items from the specified container.

        Parameters:
        container (str): The name of the container to clear.
        """
        database = client.get_database_client("articles")
        container = database.get_container_client("articles")
        logging.info(f"Clearing all items from the container '{container.id}'.")
        try:
            items = list(container.read_all_items())
            total_items = len(items)

            # Logging the number of items before deletion
            if total_items > 0:
                logging.info(
                    f"Found {total_items} items in the container. Deleting them now."
                )
            else:
                logging.info("No items found in the container. Nothing to delete.")

            # Using tqdm for progress tracking during deletion
            for item in tqdm(
                items, desc=f"Deleting items from '{container.id}'", unit="item"
            ):
                container.delete_item(item, partition_key=item["id"])
                logging.info(f"Deleted item with ID: {item['id']}")

            logging.info(
                f"Successfully cleared all items from the container '{container.id}'."
            )

        except Exception as e:
            logging.error(f"Error clearing container '{container.id}': {e}")
