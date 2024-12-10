import logging
from googlesearch import search
from tqdm import tqdm
from urllib.parse import urlparse


def google_search_article_links(title: str, num_results: int = 2) -> list:
    """
    Searches Google for articles similar to the given title and ensures domain diversity.

    Parameters:
    title (str): The title of the article to search for.
    num_results (int): The number of search results to return (default is 10).

    Returns:
    list: A list of URLs of diverse articles.
    """
    query = title
    links = []
    seen_domains = set()

    logging.info(f"Starting Google search for the query: '{query}'")

    try:
        # Perform the search and gather the links
        search_results = search(query, num_results=num_results)

        for link in tqdm(search_results, desc="Gathering links", unit="link"):
            parsed_url = urlparse(link)
            domain = parsed_url.netloc

            # Check if the base domain is already seen
            if domain not in seen_domains:
                logging.info(f"Adding link: {link}")
                links.append(link)
                seen_domains.add(domain)
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
            additional_results = search(additional_query, num_results=remaining_results)

            for link in additional_results:
                parsed_url = urlparse(link)
                domain = parsed_url.netloc

                if domain not in seen_domains:
                    logging.info(f"Adding additional link: {link}")
                    links.append(link)
                    seen_domains.add(domain)

        logging.info(f"Successfully gathered {len(links)} diverse links.")

    except Exception as e:
        logging.error(f"An error occurred during the Google search: {e}")

    logging.info(f"Total diverse links gathered: {len(links)}")
    return links
