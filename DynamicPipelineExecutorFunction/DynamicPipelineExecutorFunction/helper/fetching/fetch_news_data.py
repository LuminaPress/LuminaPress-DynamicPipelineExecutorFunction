import logging
import requests
from tqdm import tqdm
from ...core.config import news_api_key, news_api_url


def fetch_news_data():
    try:
        logging.info("Starting to fetch top headlines from News API.")
        response = requests.get(
            news_api_url, params={"country": "us", "apiKey": news_api_key}
        )
        response.raise_for_status()  # Raise an exception for 4xx/5xx HTTP status codes

        news_data = response.json()

        if news_data["status"] == "ok":
            articles = news_data["articles"]
            logging.info(
                f"Successfully fetched {len(articles)} articles from the News API."
            )

            # Add tqdm progress bar to track processing of articles (if large amount)
            for article in tqdm(articles, desc="Processing Articles", unit="article"):
                # You can add specific processing logic here for each article if needed
                pass

            logging.info(f"Processed {len(articles)} articles.")
            return articles
        else:
            logging.error(f"News API returned an error: {news_data}")
            return []
    except requests.RequestException as e:
        logging.error(f"Error fetching data from News API: {e}")
        return []
