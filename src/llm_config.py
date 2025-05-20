# llm_config.py

import os
from dotenv import load_dotenv

# Force load .env from project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

from openai import AzureOpenAI

endpoint = "https://abutair-opeani.openai.azure.com/"
model_name = "gpt-4o"
deployment = "gpt-4o"
api_version = "2024-12-01-preview"
client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key='KQMWD5tNt0L0zJClubu4zuJN6uUpVpe2gb9uFzD5SChcKDWUX0NzJQQJ99AKACYeBjFXJ3w3AAABACOGR2Ms',
)
# LLM model to be used
llm_model = 'gpt-4o'
