Open Perplex: A Perplexity AI Alternative
=========================================

🚀 Project Overview
-------------------

Open Perplex is an open-source alternative to Perplexity AI, designed to provide concise, sourced answers to user queries by leveraging search results and a powerful Large Language Model (LLM). It features a responsive web interface built with HTML, Tailwind CSS, and JavaScript, backed by a FastAPI Python backend.

The application fetches real-time search results, extracts relevant context, and then uses an LLM (currently configured for Groq API with `llama3-8b-8192`) to synthesize an answer, complete with source attribution and follow-up questions.

✨ Features
----------

-   Intelligent Answering: Get direct, summarized answers to your questions.

-   Source Attribution: View the top search results used to generate the answer.

-   Related Questions: Discover follow-up questions to deepen your understanding.

-   Pro Mode: Enable more detailed web scraping of top search results for richer context (requires Serper API).

-   Responsive UI: A clean, intuitive interface that works seamlessly on both desktop and mobile devices.

-   FastAPI Backend: Robust and scalable Python backend for handling search and LLM interactions.

-   Vercel Deployment Ready: Optimized for easy deployment as serverless functions on Vercel.

🛠️ Technologies Used
---------------------

Frontend:

-   HTML: Structure of the web page.

-   Tailwind CSS: Utility-first CSS framework for rapid and responsive styling.

-   JavaScript: Powers interactive elements, API calls, and dynamic content rendering.

-   Marked.js: For rendering Markdown content (LLM answers) on the frontend.

Backend:

-   FastAPI: High-performance web framework for building the API.

-   Python: Core programming language.

-   `python-dotenv`: (For local development) Manages environment variables.

-   Groq API : For Large Language Model (LLM) inference.

    -   Currently configured for `llama3-8b-8192` (Groq).

-   Serper API: For fetching real-time Google search results.

-   `langchain-community` / `langchain-huggingface` / `groq`: Python libraries for interacting with LLMs and web scraping tools.

-   `orjson`: Faster JSON serialization.

-   `requests`: For making HTTP requests to external APIs.

-   `RecursiveCharacterTextSplitter` (from LangChain): For intelligent text chunking.

Deployment:

-   Vercel: Serverless platform for hosting both frontend and backend.

⚙️ Setup Instructions
---------------------

Follow these steps to get Open Perplex running locally on your machine.

### 1\. Clone the Repository

```bash
git clone https://github.com/bassemalyyy/Open-Perplex.git
cd Open-Perplex
```

### 2\. Set up Environment Variables

You'll need API keys for Serper (for search) and either Groq or Hugging Face (for the LLM).

1.  Get API Keys:

    -   Serper API: Sign up at <https://serper.dev/> to get your API key.

    -   Groq API: Sign up at <https://console.groq.com/keys> to get your API key.

2.  Create .env file:

    In the root directory of your project (where vercel.json is), create a file named .env and add your API keys:

    ```bash
    # .env
    SERPER_API_KEY=YOUR_SERPER_API_KEY_HERE
    GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE
    ```

    Important: Replace `YOUR_SERPER_API_KEY_HERE`, `YOUR_GROQ_API_KEY_HERE`, with your actual keys. Do NOT commit this `.env` file to Git! It's already included in `.gitignore`.

### 3\. Backend Setup

The backend is a FastAPI application.

1.  Navigate to the `api` directory:

    ```bash
    cd api
    ```

2.  Create a Python Virtual Environment:

    ```bash
    python3 -m venv venv
    ```

3.  Activate the Virtual Environment:

    -   On Windows (Git Bash/CMD):

        ```bash
        source venv/Scripts/activate
        ```

4.  Install Python Dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5.  Run the FastAPI Backend:

    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

    The backend will start on http://localhost:8000.

### 4\. Frontend Setup

The frontend is a static HTML file.

1.  Open index.html:

    Simply open the index.html file located in the root of your project in your web browser.

    -   Note: For the frontend to communicate with the backend, the backend must be running (as per step 3.5). The `index.html` is configured to fetch from `/api/search`, which works both locally (if you configure a proxy or use a full URL) and when deployed to Vercel. For local testing with `uvicorn`, ensure your browser allows requests to `http://localhost:8000`.

🚀 Deployment to Vercel
-----------------------

This project is configured for easy deployment to Vercel.

1.  Project Structure:

    Ensure your project structure matches the Vercel standard:

    ```bash
    open-perplex/
    ├── api/
    │   ├── __init__.py      # Empty file to make 'api' a Python package
    │   ├── index.py         # from main import app
    │   ├── groq_llm.py    # LLM setup file
    │   ├── build_context.py
    │   ├── semantic_chunking.py
    │   ├── sources_manipulation.py
    │   ├── sources_searcher.py
    │   ├── prompts.py
    ├── .env                 # Only for local development
    ├── requirements.txt
    ├── vercel.json          # Vercel configuration file
    ├── index.html           # Your frontend
    ```

2.  vercel.json Configuration:

    Ensure your vercel.json is in the root of your project with the following content:

    ```bash
    {
      "version": 2,
      "builds": [
        {
          "src": "api/index.py",
          "use": "@vercel/python"
        },
        {
          "src": "index.html",
          "use": "@vercel/static"
        }
      ],
      "routes": [
        {
          "src": "/api/(.*)",
          "dest": "/api/index.py"
        },
        {
          "src": "/(.*)",
          "dest": "/index.html"
        }
      ]
    }
    ```

3.  Vercel Environment Variables:

    This is critical for Vercel deployment. You must add your API keys directly in the Vercel dashboard:

    -   Go to your Vercel Dashboard -> Select your Project -> Settings -> Environment Variables.

    -   Add `SERPER_API_KEY` and `GROQ_API_KEY` with their respective values.

4.  Deploy:

    -   Via Git: Connect your GitHub (or other Git provider) repository to Vercel. Vercel will automatically detect the `vercel.json` and deploy your project. Subsequent pushes to your `main` branch will trigger automatic redeployments.

    -   Via Vercel CLI:

        ```bash
        npm install -g vercel # If not already installed
        vercel login
        vercel deploy
        ```

        Follow the prompts.

💡 Usage
--------

1.  Type your query into the "Ask anything..." input field.

2.  (Optional) Check "Pro Mode" for more in-depth search and scraping.

3.  (Optional) Select a location for localized search results.

4.  Click "Search" or press Enter.

5.  The AI's answer, sources, and related questions will appear dynamically.

6.  Click on a related question to initiate a new search.

🤝 Contributing
---------------

Contributions are welcome! If you have suggestions for improvements, new features, or bug fixes, please open an issue or submit a pull request.