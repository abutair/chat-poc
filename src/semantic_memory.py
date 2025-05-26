
import numpy as np
import streamlit as st
from embedding_client import embedding_client, embedding_model

def init_semantic_memory():
    """Initialize in-memory semantic storage."""
    if "semantic_memory" not in st.session_state:
        st.session_state.semantic_memory = []

def embed_text(text):
    """Embed a piece of text using OpenAI's embedding model."""
    try:
        response = embedding_client.embeddings.create(
            model=embedding_model,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

def save_message_embedding(role, message):
    """Save a message to in-memory semantic storage."""
    embedding = embed_text(message)
    if embedding is None:
        return  # Skip if embedding fails
    
    record = {
        "role": role,
        "message": message,
        "embedding": np.array(embedding)
    }
    st.session_state.semantic_memory.append(record)
    
    # Optional: Limit memory size to prevent memory issues
    max_memory_size = 1000  # Keep last 1000 messages
    if len(st.session_state.semantic_memory) > max_memory_size:
        st.session_state.semantic_memory = st.session_state.semantic_memory[-max_memory_size:]

def find_similar_messages(query, top_k=5):
    """Find top_k most semantically similar past messages."""
    if not st.session_state.semantic_memory:
        return []
    
    query_embedding = embed_text(query)
    if query_embedding is None:
        return []
    
    query_embedding = np.array(query_embedding)
    
    similarities = []
    for record in st.session_state.semantic_memory:
        try:
            similarity = cosine_similarity(query_embedding, record["embedding"])
            similarities.append((similarity, record))
        except Exception:
            continue  # Skip corrupted records
    
    # Sort by similarity descending
    similarities.sort(reverse=True, key=lambda x: x[0])
    
    # Return top-k records in OpenAI chat format
    return [{"role": r["role"], "content": r["message"]} for _, r in similarities[:top_k]]

def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    try:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    except:
        return 0.0

def clear_semantic_memory():
    """Clear semantic memory."""
    st.session_state.semantic_memory = []