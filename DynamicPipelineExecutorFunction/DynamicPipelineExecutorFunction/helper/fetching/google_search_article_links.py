import logging
from googlesearch import search
from tqdm import tqdm
from urllib.parse import urlparse
from .get_page_date import get_page_date


def google_search_article_links(
    title: str, num_results: int = 2, existing_links: list = None
) -> list:
    """
    Searches Google for articles similar to the given title and ensures domain diversity.

    Parameters:
    title (str): The title of the article to search for.
    num_results (int): The number of search results to return (default is 2).
    existing_links (list, optional): List of existing links to avoid duplicating domains.

    Returns:
    list: A list of unique URLs of diverse articles with valid dates.
    """
    # Initialize existing links if not provided
    existing_links = existing_links or []
    links = []

    # Create a set of domains from existing links to ensure uniqueness
    seen_domains = {urlparse(link).netloc for link in existing_links}

    query = title
    logging.info(f"Starting Google search for the query: '{query}'")

    try:
        # Perform the search and gather the links
        search_results = search(
            query, num_results=num_results * 3
        )  # Search more to account for filtering

        for link in tqdm(search_results, desc="Gathering links", unit="link"):
            if len(links) >= num_results:
                break

            parsed_url = urlparse(link)
            domain = parsed_url.netloc

            # Check if the base domain is already seen
            if domain not in seen_domains:
                try:
                    # Validate the page date
                    if get_page_date(link):
                        logging.info(f"Adding link: {link}")
                        links.append(link)
                        seen_domains.add(domain)
                    else:
                        logging.info(f"Skipping link without date: {link}")
                except Exception as e:
                    logging.error(f"Error processing link {link}: {e}")
            else:
                logging.info(f"Skipping duplicate domain: {domain}")

        # If we don't have enough links, refine the search
        if len(links) < num_results:
            logging.warning(
                f"Insufficient diverse links gathered ({len(links)}). Refining search."
            )
            # Perform a new search excluding already seen domains
            remaining_results = num_results - len(links)
            additional_query = f"{query} -site:{' -site:'.join(seen_domains)}"
            additional_results = search(
                additional_query, num_results=remaining_results * 3
            )

            for link in additional_results:
                if len(links) >= num_results:
                    break

                parsed_url = urlparse(link)
                domain = parsed_url.netloc

                if domain not in seen_domains:
                    try:
                        # Validate the page date
                        if get_page_date(link):
                            logging.info(f"Adding additional link: {link}")
                            links.append(link)
                            seen_domains.add(domain)
                        else:
                            logging.info(
                                f"Skipping additional link without date: {link}"
                            )
                    except Exception as e:
                        logging.error(f"Error processing additional link {link}: {e}")

        logging.info(f"Successfully gathered {len(links)} diverse links with dates.")

    except Exception as e:
        logging.error(f"An error occurred during the Google search: {e}")

    # Combine and return unique links
    return links
