import os
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Azure Cosmos DB configuration from environment variables
cosmos_endpoint = os.getenv("COSMOS_ENDPOINT")
cosmos_key = os.getenv("COSMOS_KEY")
# News API configuration from environment variables
news_api_url = os.getenv("NEWS_API_URL")
news_api_key = os.getenv("NEWS_API_KEY")

# Initialize CosmosClient
client = CosmosClient(cosmos_endpoint, cosmos_key)

# Example of setting headers (this part remains unchanged)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com",  # Simulates referral from Google search
}
