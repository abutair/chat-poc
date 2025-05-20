# semantic_memory.py (fixed)

import os
import json
import numpy as np
from dotenv import load_dotenv
from embedding_client import embedding_client, embedding_model

load_dotenv()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEMANTIC_MEMORY_FILE = os.path.join(PROJECT_ROOT, "memory", "semantic_memory.json")

def init_semantic_memory():
    """Ensure semantic memory file exists."""
    os.makedirs(os.path.join(PROJECT_ROOT, "memory"), exist_ok=True)
    if not os.path.exists(SEMANTIC_MEMORY_FILE):
        with open(SEMANTIC_MEMORY_FILE, "w") as f:
            json.dump([], f)

def embed_text(text):
    """Embed a piece of text using OpenAI's embedding model."""
    response = embedding_client.embeddings.create(
        model=embedding_model,
        input=text
    )
    return response.data[0].embedding

def save_message_embedding(role, message):
    """Save a message (role + text + embedding) to semantic memory."""
    embedding = embed_text(message)
    record = {
        "role": role,
        "message": message,  # Storing internally as 'message' for backward compatibility
        "embedding": embedding
    }

    try:
        with open(SEMANTIC_MEMORY_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(record)

    with open(SEMANTIC_MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def find_similar_messages(query, top_k=5):
    """Find top_k most semantically similar past messages."""
    query_embedding = np.array(embed_text(query))

    try:
        with open(SEMANTIC_MEMORY_FILE, "r") as f:
            records = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    similarities = []
    for record in records:
        record_embedding = np.array(record["embedding"])
        similarity = cosine_similarity(query_embedding, record_embedding)
        similarities.append((similarity, record))

    # Sort by similarity descending
    similarities.sort(reverse=True, key=lambda x: x[0])

    # Return top-k records, MAPPING 'message' to 'content' for OpenAI
    top_records = [{"role": r["role"], "content": r["message"]} for _, r in similarities[:top_k]]
    return top_records

def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def clear_semantic_memory():
    """Clear semantic memory."""
    with open(SEMANTIC_MEMORY_FILE, "w") as f:
        json.dump([], f)
