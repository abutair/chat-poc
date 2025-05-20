# buffer_memory.py

import json
import streamlit as st

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAT_HISTORY_FILE = os.path.join(PROJECT_ROOT, "memory", "chat_history.json")

def init_chat_history():
    if "chat_history" not in st.session_state:
        try:
            with open(CHAT_HISTORY_FILE, "r") as f:
                contents = f.read().strip()
                st.session_state.chat_history = json.loads(contents) if contents else []
        except (json.JSONDecodeError, FileNotFoundError):
            st.session_state.chat_history = []


def save_chat_history():
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(st.session_state.chat_history, f)


def clear_chat_history():
    st.session_state.chat_history = []
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump([], f)


def build_context_messages(chat_history, max_turns=10):
    """
    Returns a list of messages formatted as OpenAI chat format:
    [{"role": "user", "content": ...}, {"role": "assistant", "content": ...}, ...]

    Only includes the last N user-assistant turns, where N = max_turns
    """
    recent = chat_history[-max_turns * 2:]  # Each turn has user + assistant
    messages = []

    for role, content in recent:
        formatted_role = "user" if role == "user" else "assistant"
        messages.append({"role": formatted_role, "content": content})

    return messages
