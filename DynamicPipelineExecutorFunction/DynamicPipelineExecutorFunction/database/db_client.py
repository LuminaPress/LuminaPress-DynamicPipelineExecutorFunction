import logging
from tqdm import tqdm
import uuid
from ..core import *


class CosmosDBClient:
    def __init__(
        self, database_name: str = "articles", container_name: str = "articles"
    ) -> None:
        logging.info(
            f"Initializing Cosmos DB Client for database: {database_name} and container: {container_name}"
        )
        self.database = client.get_database_client(database_name)
        self.container = self.database.get_container_client(container_name)

    # CREATE: Add a new item to the container
    def create_item(self, item_data: dict):
        try:
            if "id" not in item_data:
                item_data["id"] = str(
                    uuid.uuid4()
                )  # Generate a unique ID if not present
            created_item = self.container.create_item(item_data)
            logging.info(f"Item created with ID: {created_item['id']}")
            return created_item
        except Exception as e:
            logging.error(f"Error creating item: {e}")
            return None

    # READ: Get an item by its ID
    def read_item(self, item_id: str, partition_key: str):
        try:
            item = self.container.read_item(item_id, partition_key)
            logging.info(f"Item retrieved: {item['id']}")
            return item
        except Exception as e:
            logging.error(f"Error reading item: {e}")
            return None

    # UPDATE: Update an existing item
    def update_item(self, item_id: str, partition_key: str, updated_data: dict):
        try:
            # Read the item first to ensure it exists
            item = self.container.read_item(item_id, partition_key)
            if item:
                # Update the item with the new data
                item.update(updated_data)
                # Replace the item in the container
                updated_item = self.container.replace_item(item_id, item)
                logging.info(f"Item updated with ID: {updated_item['id']}")
                return updated_item
            else:
                logging.warning(f"Item with ID {item_id} not found.")
                return None
        except Exception as e:
            logging.error(f"Error updating item: {e}")
            return None

    # DELETE: Delete an item
    def delete_item(self, item_id: str, partition_key: str):
        try:
            # Read the item first to ensure it exists
            item = self.container.read_item(item_id, partition_key)
            if item:
                self.container.delete_item(item_id, partition_key)
                logging.info(f"Item with ID {item_id} deleted.")
                return True
            else:
                logging.warning(f"Item with ID {item_id} not found.")
                return False
        except Exception as e:
            logging.error(f"Error deleting item: {e}")
            return False

    # Get all items in the container
    def get_all_items(self):
        try:
            query = "SELECT * FROM c"  # Simple query to get all items
            items = list(
                self.container.query_items(query, enable_cross_partition_query=True)
            )
            logging.info(f"Retrieved {len(items)} items.")
            return items
        except Exception as e:
            logging.error(f"Error retrieving items: {e}")
            return []

    # Get all items with progress tracking
    def get_all_items_with_progress(self):
        try:
            query = "SELECT * FROM c"
            items = list(
                self.container.query_items(query, enable_cross_partition_query=True)
            )

            logging.info(f"Retrieved {len(items)} items. Starting progress tracking...")

            # Using tqdm to show a progress bar while processing items
            for item in tqdm(items, desc="Processing items", unit="item"):
                logging.debug(
                    f"Processing item with ID: {item['id']}"
                )  # Log each item being processed

            logging.info("All items processed successfully.")
            return items
        except Exception as e:
            logging.error(f"Error retrieving items with progress: {e}")
            return []

    # Delete multiple items with progress tracking
    def delete_multiple_items(self, item_ids: list, partition_key: str):
        try:
            logging.info(f"Starting to delete {len(item_ids)} items.")

            # Using tqdm for progress tracking while deleting items
            for item_id in tqdm(item_ids, desc="Deleting items", unit="item"):
                self.delete_item(item_id, partition_key)

            logging.info(f"Successfully deleted {len(item_ids)} items.")
        except Exception as e:
            logging.error(f"Error deleting multiple items: {e}")

    def query(self, query, **kwargs):
        return self.container.query_items(query, **kwargs)
