import os
import requests
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants for Serper API
API_URL = "https://google.serper.dev/search"
API_KEY = os.getenv("SERPER_API_KEY") # Ensure SERPER_API_KEY is set in your .env file
DEFAULT_LOCATION = 'us'
HEADERS = {
    'X-API-KEY': API_KEY,
    'Content-Type': 'application/json'
}


def get_sources(query: str, pro_mode: bool = False, stored_location: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetches search results from the Serper API. This is an external API and is
    necessary for providing real-time search capabilities, similar to Perplexity.

    :param query: The search query string.
    :param pro_mode: Boolean flag to determine the number of search results (more for pro_mode).
    :param stored_location: Optional location string (e.g., 'us', 'gb') for localized search.
    :return: A dictionary containing parsed search results (organic, topStories, images, graph, answerBox).
             Returns an empty dictionary on error or if API key is missing.
    """
    if not API_KEY:
        logger.error("SERPER_API_KEY environment variable is not set. Cannot fetch search results.")
        return {}

    try:
        search_location = (stored_location or DEFAULT_LOCATION).lower()
        # Adjust number of results based on pro_mode
        num_results = 10 if pro_mode else 20

        payload = {
            "q": query,
            "num": num_results,
            "gl": search_location # Geographic location for search results
        }

        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        data = response.json()

        # Extract and return relevant fields from the Serper API response
        return {
            'organic': extract_fields(data.get('organic', []), ['title', 'link', 'snippet', 'date']),
            'topStories': extract_fields(data.get('topStories', []), ['title', 'imageUrl']),
            'images': extract_fields(data.get('images', [])[:6], ['title', 'imageUrl']), # Limit images to top 6
            'graph': data.get('knowledgeGraph'), # Knowledge graph data
            'answerBox': data.get('answerBox') # Answer box data
        }

    except requests.RequestException as e:
        logger.error(f"HTTP error while getting sources from Serper API: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error while getting sources: {e}")

    return {}


def extract_fields(items: List[Dict[str, Any]], fields: List[str]) -> List[Dict[str, Any]]:
    """
    Helper function to extract specified fields from a list of dictionaries.

    :param items: List of dictionaries (e.g., list of organic results).
    :param fields: List of string keys representing the fields to extract.
    :return: A new list of dictionaries, where each dictionary only contains the specified fields.
    """
    return [{key: item[key] for key in fields if key in item} for item in items]