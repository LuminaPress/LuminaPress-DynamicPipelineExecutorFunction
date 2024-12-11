# import requests
# from bs4 import BeautifulSoup


# def get_last_modified(url):
#     """Get the last modified date from HTTP headers."""
#     try:
#         response = requests.head(url, timeout=10)
#         last_modified = response.headers.get("Last-Modified")
#         if last_modified:
#             return f"Last Modified: {last_modified}"
#     except requests.RequestException as e:
#         return f"Error in getting Last-Modified: {e}"
#     return "Last-Modified header not available."


# def get_metadata_date(url):
#     """Get the date from metadata in the HTML source."""
#     try:
#         response = requests.get(url, timeout=10)
#         soup = BeautifulSoup(response.text, "html.parser")
#         # Common metadata tags for dates
#         for tag in ["datePublished", "dateModified", "dateCreated"]:
#             date = soup.find(attrs={"property": tag}) or soup.find(attrs={"name": tag})
#             if date and date.get("content"):
#                 return f"Metadata Date: {date.get('content')}"
#     except requests.RequestException as e:
#         return f"Error in fetching metadata: {e}"
#     return "Metadata Date not found."


# def get_wayback_date(url):
#     """Get the first archive date from the Wayback Machine."""
#     try:
#         wayback_api = f"http://archive.org/wayback/available?url={url}"
#         response = requests.get(wayback_api, timeout=10).json()
#         snapshots = response.get("archived_snapshots", {}).get("closest")
#         if snapshots:
#             timestamp = snapshots["timestamp"]  # Format: YYYYMMDDHHMMSS
#             # Convert timestamp to a readable format
#             formatted_date = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]}"
#             return f"Wayback Date: {formatted_date}"
#     except requests.RequestException as e:
#         return f"Error in fetching Wayback Machine data: {e}"
#     return "Wayback Date not found."


# def get_page_date(url):
#     """Combines all methods to retrieve the date."""
#     # 1. Try HTTP headers
#     last_modified = get_last_modified(url)
#     if "not available" not in last_modified and "Error" not in last_modified:
#         return False

#     # 2. Try metadata
#     metadata_date = get_metadata_date(url)
#     if "not found" not in metadata_date and "Error" not in metadata_date:
#         return False

#     # 3. Try Wayback Machine
#     wayback_date = get_wayback_date(url)
#     if "not found" not in wayback_date and "Error" not in wayback_date:
#         return False

#     return True
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import dateutil.parser


def get_last_modified(url):
    """Get the last modified date from HTTP headers."""
    try:
        response = requests.head(url, timeout=10)
        last_modified = response.headers.get("Last-Modified")
        if last_modified:
            try:
                parsed_date = dateutil.parser.parse(last_modified)
                return parsed_date.date()
            except (ValueError, TypeError):
                return None
    except requests.RequestException:
        return None
    return None


def get_metadata_date(url):
    """Get the date from metadata in the HTML source."""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        # Common metadata tags for dates
        for tag in ["datePublished", "dateModified", "dateCreated"]:
            date_tag = soup.find(attrs={"property": tag}) or soup.find(
                attrs={"name": tag}
            )
            if date_tag and date_tag.get("content"):
                try:
                    parsed_date = dateutil.parser.parse(date_tag.get("content"))
                    return parsed_date.date()
                except (ValueError, TypeError):
                    pass
    except requests.RequestException:
        return None
    return None


def get_wayback_date(url):
    """Get the first archive date from the Wayback Machine."""
    try:
        wayback_api = f"http://archive.org/wayback/available?url={url}"
        response = requests.get(wayback_api, timeout=10).json()
        snapshots = response.get("archived_snapshots", {}).get("closest")
        if snapshots:
            timestamp = snapshots["timestamp"]  # Format: YYYYMMDDHHMMSS
            try:
                # Convert timestamp to date
                parsed_date = datetime.strptime(timestamp[:8], "%Y%m%d").date()
                return parsed_date
            except (ValueError, TypeError):
                return None
    except requests.RequestException:
        return None
    return None


def get_page_date(url):
    """
    Combines all methods to retrieve the date.
    Ensures the retrieved date is not today's date.

    Returns:
    bool: True if a valid historical date is found, False otherwise
    """
    today = date.today()

    # 1. Try HTTP headers
    last_modified_date = get_last_modified(url)
    if last_modified_date and last_modified_date != today:
        return False

    # 2. Try metadata
    metadata_date = get_metadata_date(url)
    if metadata_date and metadata_date != today:
        return False

    # 3. Try Wayback Machine
    wayback_date = get_wayback_date(url)
    if wayback_date and wayback_date != today:
        return False

    return True
