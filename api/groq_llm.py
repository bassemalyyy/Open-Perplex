# import json
# import os
# import ollama # Import the ollama client
# from langchain_core.prompts import PromptTemplate
# from perplex.prompts import search_prompt_system, relevant_prompt_system

# # Use ENV variables or set a default model for Ollama
# # Ensure you have this model pulled locally (e.g., 'ollama pull llama3')
# MODEL = os.getenv("OLLAMA_MODEL", "llama3.2") 

# def get_answer(query, contexts, date_context):
#     """
#     Generates an answer using the Ollama local LLM, streaming the response.

#     :param query: The user's question.
#     :param contexts: Relevant contexts gathered from search results.
#     :param date_context: Current date for contextualization.
#     :return: A generator yielding chunks of the LLM's answer.
#     """
#     system_prompt_search = PromptTemplate(input_variables=["date_today"], template=search_prompt_system)

#     messages = [
#         {"role": "system", "content": system_prompt_search.format(date_today=date_context)},
#         {"role": "user", "content": "User Question : " + query + "\n\n CONTEXTS :\n\n" + contexts}
#     ]

#     try:
#         # Call Ollama chat API with streaming
#         stream = ollama.chat(
#             model=MODEL,
#             messages=messages,
#             stream=True,
#         )

#         for chunk in stream:
#             # Extract content from the streamed chunk
#             if chunk['message']['content'] is not None:
#                 yield chunk['message']['content']

#     except Exception as e:
#         print(f"Error during get_answer_ollama call: {e}")
#         # Yield an error message formatted as SSE data
#         yield json.dumps(
#             {'type': 'error', 'data': "We are currently experiencing some issues with Ollama. Please ensure it's running and the model is available."}) + "\n\n"


# def get_relevant_questions(contexts, query):
#     """
#     Generates relevant follow-up questions using the Ollama local LLM.

#     :param contexts: Relevant contexts.
#     :param query: The original user query.
#     :return: A JSON string containing an array of follow-up questions.
#     """
#     try:
#         messages = [
#             {"role": "system",
#              "content": relevant_prompt_system
#              },
#             {"role": "user",
#              "content": "User Query: " + query + "\n\n" + "Contexts: " + "\n" + contexts + "\n"}
#         ]

#         # Call Ollama chat API for a non-streaming JSON response
#         response = ollama.chat(
#             model=MODEL,
#             messages=messages,
#             format="json" # Request JSON format from Ollama
#         )
#         # Ollama returns the JSON string within the 'content' field of the message
#         return response['message']['content']
#     except Exception as e:
#         print(f"Error during RELEVANT OLLAMA ***************: {e}")
#         # Return an empty JSON array for follow-up questions on error
#         return json.dumps({"followUp": []})

import json
import os
import logging
from langchain_core.prompts import PromptTemplate
from groq import Groq
from api.prompts import search_prompt_system, relevant_prompt_system
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Groq API Configuration
# Using llama3-8b-8192 which is one of the cheapest models on Groq
GROQ_MODEL = "llama3-8b-8192"  # Cheapest model available
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Get from environment variable

# Initialize Groq client
try:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in your .env file.")
    
    client = Groq(api_key=GROQ_API_KEY)
    logger.info(f"Groq client initialized with model: {GROQ_MODEL}")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    client = None

def get_answer(query, contexts, date_context):
    """
    Generates an answer using the Groq API, streaming the response.

    :param query: The user's question.
    :param contexts: Relevant contexts gathered from search results.
    :param date_context: Current date for contextualization.
    :return: A generator yielding chunks of the LLM's answer.
    """
    if client is None:
        # Fallback response when Groq client is not available
        logger.warning("Groq client not initialized, providing fallback response")
        fallback_response = f"Based on the available information about '{query}', here's what I found from the search results:\n\n{contexts[:500]}..."
        yield fallback_response
        return

    system_prompt_search = PromptTemplate(input_variables=["date_today"], template=search_prompt_system)

    messages = [
        {
            "role": "system", 
            "content": system_prompt_search.format(date_today=date_context)
        },
        {
            "role": "user", 
            "content": "User Question: " + query + "\n\nCONTEXTS:\n\n" + contexts
        }
    ]

    try:
        logger.info("Sending streaming request to Groq API for answer generation...")
        
        # Call Groq chat API with streaming
        stream = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            stream=True,
            max_tokens=1024,
            temperature=0.7,
        )

        for chunk in stream:
            # Extract content from the streamed chunk
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    except Exception as e:
        logger.exception(f"Error during Groq API call for answer: {e}")
        # Provide a fallback response with search context
        fallback_response = f"I encountered an issue processing your question about '{query}'. Based on the search results: {contexts[:300]}..."
        yield fallback_response


def get_relevant_questions(contexts, query):
    """
    Generates relevant follow-up questions using the Groq API.

    :param contexts: Relevant contexts.
    :param query: The original user query.
    :return: A JSON string containing an array of follow-up questions.
    """
    if client is None:
        # Provide some default relevant questions
        default_questions = [
            f"What are the latest developments regarding {query}?",
            f"How does {query} compare to similar topics?",
            f"What are the implications of {query}?"
        ]
        return json.dumps({"followUp": default_questions})

    messages = [
        {
            "role": "system",
            "content": relevant_prompt_system
        },
        {
            "role": "user",
            "content": "User Query: " + query + "\n\nContexts: " + contexts[:1000] + "\n"
        }
    ]

    try:
        logger.info("Sending request to Groq API for relevant questions...")
        
        # Call Groq chat API for a non-streaming JSON response
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=512,
            temperature=0.3,  # Lower temperature for more consistent JSON output
        )
        
        generated_text = response.choices[0].message.content.strip()
        
        if generated_text:
            try:
                # Try to extract JSON from the response
                if "{" in generated_text and "}" in generated_text:
                    json_start = generated_text.find("{")
                    json_end = generated_text.rfind("}") + 1
                    json_str = generated_text[json_start:json_end]
                    
                    # Validate JSON
                    parsed_json = json.loads(json_str)
                    if "followUp" in parsed_json and isinstance(parsed_json["followUp"], list):
                        return json.dumps(parsed_json)
                
                # If no valid JSON found, create questions from the response
                fallback_questions = [
                    f"Tell me more about {query}",
                    f"What are the recent updates on {query}?",
                    f"How significant is {query}?"
                ]
                return json.dumps({"followUp": fallback_questions})
                
            except json.JSONDecodeError:
                logger.warning(f"Groq API did not return valid JSON for relevant questions")
                fallback_questions = [
                    f"What else should I know about {query}?",
                    f"Are there recent developments in {query}?",
                    f"What are the key aspects of {query}?"
                ]
                return json.dumps({"followUp": fallback_questions})
        else:
            logger.warning("No text generated for relevant questions.")
            return json.dumps({"followUp": []})

    except Exception as e:
        logger.exception(f"Error during Groq API call for relevant questions: {e}")
        # Return fallback questions
        fallback_questions = [
            f"What are the main points about {query}?",
            f"Can you provide more details on {query}?",
            f"What should I know about {query}?"
        ]
        return json.dumps({"followUp": fallback_questions})
