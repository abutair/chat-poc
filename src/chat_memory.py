# chat_memory.py

from buffer_memory import (init_chat_history, save_chat_history,
                           build_context_messages, clear_chat_history)
from semantic_memory import init_semantic_memory, clear_semantic_memory, find_similar_messages

import streamlit as st


def init_memory():
    """Initialize all memory layers"""
    init_chat_history()
    init_semantic_memory()

def clear_memory():
    """Clear all memory layers"""
    clear_chat_history()
    clear_semantic_memory()

def save_memory():
    """Save all memory layers to disk"""
    save_chat_history()


def build_context(user_question):
    """Build conversation context using both buffer memory and semantic memory."""

    # 1. Get recent chat history (buffer memory)
    buffer_messages = build_context_messages(st.session_state.chat_history, max_turns=10)

    # 2. Get top-k similar past messages (semantic memory)
    semantic_messages = find_similar_messages(user_question, top_k=5)

    # 3. Merge semantic first, then buffer memory (older first)
    full_context = semantic_messages + buffer_messages

    return full_context
