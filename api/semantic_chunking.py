from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize a text splitter for general-purpose chunking.
# Adjust chunk_size and chunk_overlap as needed for optimal context feeding to the LLM.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # Each chunk will aim for around 500 characters
    chunk_overlap=50, # Overlap between chunks to maintain context
    length_function=len, # Use standard Python len() for length calculation
    is_separator_regex=False, # Separators are not treated as regex
)

def get_chunking(text: str) -> list[str]:
    """
    Splits the provided text into meaningful chunks using RecursiveCharacterTextSplitter.
    This replaces the previous Cohere-based semantic chunking.

    Args:
    text (str): The text to be chunked.

    Returns:
    list: A list of text chunks. Returns the original text in a list if it's too short
          to chunk effectively, or an empty list if the input text is empty.
    """
    try:
        # Only perform chunking if the text is substantial enough
        if not text or len(text) < 200:
            return [text] if text else []

        # Split the text into chunks
        chunks = text_splitter.split_text(text)
        return chunks

    except Exception as e:
        logger.error(f"Error during chunking process: {e}")
        return []