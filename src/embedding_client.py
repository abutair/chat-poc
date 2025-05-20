# embedding_client.py

import os
from dotenv import load_dotenv

# Force load .env from project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

from openai import OpenAI

# Create an OpenAI Client only for embeddings
embedding_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),  # Securely load from environment
    base_url=os.getenv("OPENAI_BASE_URL")  # Securely load from environment
)

# Embedding model name
embedding_model = os.getenv("EMBEDDING_MODEL")
