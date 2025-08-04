import logging
from perplex.api.semantic_chunking import get_chunking # Updated import for simplified chunking

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def build_context(sources_result, query, pro_mode, date_context):
    """
      Build context from search results. This function now uses simplified chunking
      and removes external reranking API calls.

      :param sources_result: Dictionary containing search results (organic, graph, answerBox, topStories).
      :param query: Search query string.
      :param pro_mode: Boolean indicating whether to use pro mode (can influence initial search results count).
      :param date_context: Date context string.
      :return: Built context as a single string, combining snippets, HTML content chunks, and other relevant info.
      """
    try:
        combined_list = []

        organic_results = sources_result.get('organic', [])
        graph = sources_result.get('graph')
        answer_box = sources_result.get('answerBox')

        # Extract snippets from organic search results
        snippets = [
            f"{item['snippet']} {item.get('date', '')}"
            for item in organic_results if 'snippet' in item  # Ensure there's always a snippet
        ]
        combined_list.extend(snippets)

        # Extract and chunk HTML content from scraped websites
        # Only process if HTML content is available and sufficiently long
        html_text = " ".join(item['html'] for item in organic_results if 'html' in item)
        if html_text is not None and len(html_text) > 200:
            combined_list.extend(get_chunking(html_text))

        # Extract titles from top stories
        if sources_result.get('topStories') is not None:
            top_stories_titles = [item['title'] for item in sources_result.get('topStories') if 'title' in item]
            combined_list.extend(top_stories_titles)

        # Add descriptions and answers from 'graph' (Knowledge Graph) and 'answerBox'
        if graph is not None:
            graph_desc = graph.get('description')
            if graph_desc:
                combined_list.append(graph_desc)

        if answer_box is not None:
            for key in ['answer', 'snippet']:
                if key in answer_box:
                    combined_list.append(answer_box[key])

        # Reranking has been removed to simplify local setup.
        # The 'pro_mode' flag can still be used in `sources_searcher` to fetch more initial results.
        final_list = combined_list

        # Join all collected context pieces into a single string
        search_contexts = "\n\n".join(final_list)
        return search_contexts
    except Exception as e:
        logger.exception(f"An error occurred while building context: {e}")
        return ""