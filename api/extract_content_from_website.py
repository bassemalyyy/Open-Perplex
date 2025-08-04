from langchain_community.document_loaders import WebBaseLoader
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_website_content(url):
    """
    Extracts and cleans the main content from a given website URL using WebBaseLoader.
    This is an external dependency but essential for web scraping.

    Args:
    url (str): The URL of the website from which to extract content.

    Returns:
    str: The first 4000 characters of the cleaned main content if it is sufficiently long
         (more than 200 characters), otherwise an empty string.
    """
    try:
        clean_text_parts = []
        loader = WebBaseLoader(url)
        data = loader.load() # Load documents from the URL

        # Aggregate content from all loaded documents
        for doc in data:
            if doc.page_content:  # Check if page_content is not None or empty
                # Replace newlines to flatten the text and append to parts list
                clean_text_parts.append(doc.page_content.replace("\n", " "))

        # Join all parts into a single string after processing
        clean_text = " ".join(clean_text_parts)

        # Return up to the first 4000 characters if the content is sufficiently long
        # This prevents feeding excessively long content to the LLM
        return clean_text[:4000] if len(clean_text) > 200 else ""

    except Exception as error:
        logger.error(f'Error extracting main content from {url}: {error}')
        return ""