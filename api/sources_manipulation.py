from .extract_content_from_website import extract_website_content
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def populate_sources(sources, num_elements):
    """
    Populates the given number of sources with their full HTML content by scraping their links.

    :param sources: A list of dictionaries, where each dictionary represents a source
                    and should contain a 'link' key.
    :param num_elements: The number of top sources to scrape.
    :return: The updated list of sources with 'html' content added to the scraped ones.
    """
    try:
        # Iterate only up to num_elements to limit scraping
        for i, source in enumerate(sources[:num_elements]):
            if not source or 'link' not in source:
                logger.warning(f"Skipping invalid source at index {i}: {source}")
                continue

            try:
                # Extract content from the website URL
                html_content = extract_website_content(source['link'])
                # Add the extracted HTML content to the source dictionary
                source['html'] = html_content
                # Update the source in the original list
                sources[i] = source
            except Exception as e:
                logger.error(f"Error extracting content from {source.get('link', 'N/A')}: {e}")
                # Continue to the next source even if one fails
                continue
    except Exception as e:
        logger.error(f"Error in populate_sources: {e}")
        return sources # Return original sources on a higher-level error

    return sources
