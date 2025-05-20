# chatbot.py
# V36
# We added embedding Model I think. I still need to test if it works
# We are fixing up the memory py files and moving the prompts into their own files.
# Removed the API Key hardcoding
#
# Pls pls pls be fixed 🤞🤞
#
# It should be fixed? 🥴
#
# It fixed
#
###############################################################
# LLM FOR TESTING   =   llama3-8b-8192              <----- Can have a log of errors when responding
# LLM FOR WORKING   =   llama-3.3-70b-versatile
# Warning: Watch out for Rate Limits or price for running
###############################################################

# Here is a Complete Emoji for Completed Tasks:    ✅

import os
from dotenv import load_dotenv
import logging
import streamlit as st
from load_file import load_filetype
from gen_code import generate_pandas_code
from structured_output import handle_structured_output
from chat_memory import init_memory, save_memory, clear_memory, build_context
from semantic_memory import save_message_embedding

# <editor-fold desc="Global Variables">
MAX_RETRIES = 2
USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

# Load the .env file from one directory above this file
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path=env_path)

# Dataset path
file_path = os.getenv("EXCEL_FILE")
all_sheets = load_filetype(file_path)

# Ensure logs folder exists
os.makedirs("../logs", exist_ok=True)

# Set up logging
logging.basicConfig(filename="../logs/error.log", level=logging.ERROR)

# </editor-fold>

# 👇 Test Injecting custom CSS to style the chat input
# This specific injection is to remove the Default Red Border and add a Blue Border
st.markdown("""
    <style>
    /* Outer container */
    div[data-testid="stChatInput"] {
        border: 2px solid #00b4d8 !important;
        border-radius: 25px !important;
        padding: 4px;
        box-shadow: none !important;
    }

    /* Remove all inherited shadows recursively */
    div[data-testid="stChatInput"] * {
        border: none !important;
    }
    /* Removes the Streamlit Options */
    /*#MainMenu {visibility: hidden;}
    header {visibility: hidden; height: 0px;}
    footer {visibility: hidden;}
    */
    [data-testid="stHeader"] a {
    display: none;
    }
    
    </style>
""", unsafe_allow_html=True)


st.title("💬 Data Analytics Chatbot")

init_memory()

with st.sidebar:
    if st.button("Clear Chat History"):
        clear_memory()
        st.rerun()

# Display existing messages
for sender, msg in st.session_state.chat_history:
    with st.chat_message(name=sender, avatar=USER_AVATAR if sender == "user" else BOT_AVATAR):
        if sender == "user":
            st.markdown(f"**You:** {msg}")
        else:
            handle_structured_output(msg, all_sheets)

# Chat input with built-in Send button
if prompt := st.chat_input("Ask a question about your data..."):
    user_question = prompt
    chatbot_output = ""
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(user_question)
    # Save user message to semantic memory
    save_message_embedding("user", user_question)


    # Build the context for the LLM using recent conversation history.
    prior_messages = build_context(user_question)
    prior_messages.append({"role": "user", "content": user_question})

    # Logging User Question and context
    logging.info(f"User question: {user_question}")
    logging.debug(f"Prior messages for context: {prior_messages}")

    # Retries if it errors
    with st.spinner("🤖 Generating response..."):
        for attempt in range(1, MAX_RETRIES + 2):
            try:
                response = generate_pandas_code(prior_messages, all_sheets)
                chatbot_output = response
                logging.info("Received response from LLM.")
                break  # ✅ Success, exit loop
            except Exception as e:
                logging.error(f"Attempt {attempt} failed with error: {e}", exc_info=True)
                if attempt == MAX_RETRIES + 1:
                    st.error("❌ Failed to generate a response after multiple attempts.")
                    st.exception(e)
                else:
                    continue  # Reload

    # Show messages immediately
    with st.chat_message("bot", avatar=BOT_AVATAR):
        rendered_output = handle_structured_output(chatbot_output, all_sheets)
        logging.info("Bot response rendered successfully.")
    # Save bot message to semantic memory
    save_message_embedding("assistant", chatbot_output)

    # Save both the user input and the raw LLM response (not the rendered label)
    st.session_state.chat_history.append(("user", user_question))
    st.session_state.chat_history.append(("bot", chatbot_output))  # Save full JSON

    # Save chat history to file
    save_memory()
