import orjson as json
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

from fastapi.responses import StreamingResponse
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq_llm import get_answer, get_relevant_questions # Changed from groq_api to ollama_api
from sources_searcher import get_sources
from build_context import build_context
from sources_manipulation import populate_sources
from mangum import Mangum  # to support AWS Lambda style (used by Vercel)


app = FastAPI()

# Configure CORS middleware to allow requests from any origin.
# In a production environment, you should restrict `allow_origins` to your frontend's domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["GET", "POST"], # Allow specified HTTP methods
    allow_headers=["*"], # Allow all headers
)

# Load environment variables again (redundant if already loaded, but safe)
load_dotenv()


@app.get("/")
def root():
    """Root endpoint for a basic health check."""
    return {"message": "hello world perplexity alternative v1"}


@app.get("/up_test")
def up_test():
    """Endpoint for deployment health checks."""
    return {"status": "ok"}


@app.get("/search")
def ask(query: str, date_context: str, stored_location: str, pro_mode: bool = False):
    """
    Main search endpoint that orchestrates fetching sources, building context,
    getting an answer from the LLM, and generating relevant follow-up questions.
    Responses are streamed using Server-Sent Events (SSE).

    :param query: The user's search query.
    :param date_context: The current date for contextualization.
    :param stored_location: The user's stored location for localized search results.
    :param pro_mode: A boolean flag to enable 'pro mode' (e.g., more detailed search/scraping).
    :return: A StreamingResponse object that sends data as Server-Sent Events.
    """
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    async def generate():
        try:
            # 1. Fetch initial search sources using Serper API
            sources_result = get_sources(query, pro_mode, stored_location)
            # Send sources data to the client
            yield f"data:{json.dumps({'type': 'sources', 'data': sources_result}).decode()}\n\n"

            # 2. Populate sources with full HTML content if pro_mode is enabled
            # This involves scraping the top 'num_elements' websites
            if sources_result.get('organic') is not None and pro_mode is True:
                # Set the number of websites to scrape: here = 2
                sources_result['organic'] = populate_sources(sources_result['organic'], 2)

            # 3. Build context for the LLM from the gathered sources
            search_contexts = build_context(sources_result, query, pro_mode, date_context)

            # 4. Get the answer from the local Ollama LLM, streaming chunks
            for chunk in get_answer(query, search_contexts, date_context):
                # Each chunk from get_answer is already the text content
                yield f"data:{json.dumps({'type': 'llm', 'text': chunk}).decode()}\n\n"

            # 5. Get relevant follow-up questions from the LLM
            try:
                relevant_questions_str = get_relevant_questions(search_contexts, query)
                relevant_json = json.loads(relevant_questions_str)
                yield f"data:{json.dumps({'type': 'relevant', 'data': relevant_json}).decode()}\n\n"
            except json.JSONDecodeError as e:
                print(f"JSON decode error in relevant questions main.py: {e}. Raw response: {relevant_questions_str}")
                yield f"data:{json.dumps({'type': 'relevant', 'data': []}).decode()}\n\n"
            except Exception as e:
                print(f"error in relevant questions main.py {e}")
                yield f"data:{json.dumps({'type': 'relevant', 'data': []}).decode()}\n\n"

            # 6. Signal completion of the stream
            yield f"data:{json.dumps({'type': 'finished', 'data': ''}).decode()}\n\n"
            yield "event: end-of-stream\ndata: null\n\n"

        except Exception as e:
            print(f"An error occurred in the generate function: {e}")
            # Send a general error message to the client if an unhandled exception occurs
            yield f"data:{json.dumps({'type': 'error', 'data': 'We are currently experiencing some issues. Please try again later.'}).decode()}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

# Needed for Vercel's serverless handler
handler = Mangum(app)
