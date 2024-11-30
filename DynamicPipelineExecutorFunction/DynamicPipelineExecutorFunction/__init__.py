import logging
from .core import *
from .database import *
from .helper import *
from .images import *
from .models import *
from .text import *
from .pipelines import *

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
database = client.get_database_client("articles")
container = database.get_container_client("articles")
