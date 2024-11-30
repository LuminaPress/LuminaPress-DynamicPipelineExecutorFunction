import threading
import logging
import azure.functions as func
from . import *
from .pipelines.pipeline_factory import *


def main(myTimer: func.TimerRequest) -> None:
    # Create database and container if not already exists
    CosmosDBHelper.create_database_if_not_exists()
    CosmosDBHelper.create_container_if_not_exists()

    # Get the database and container clients
    database = client.get_database_client("articles")
    container = database.get_container_client("articles")

    PipelineFactory.execute_pipeline("update", container=container)
    PipelineFactory.execute_pipeline("process")

    # No need to return anything in a timer-triggered function
    logging.info("Database update and article fetching completed.")
