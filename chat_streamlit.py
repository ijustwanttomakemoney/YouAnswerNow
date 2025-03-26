# chat_streamlit.py
import streamlit as st
import requests

# Set your backend URL (update as needed for your deployed backend)
BACKEND_URL = "https://youanswernow.onrender.com"

st.title("Chat with the Persona-Based Bot")

# Initialize session state for conversation
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def send_message(message):
    payload = {
        "conversation_id": st.session_state.conversation_id,
        "message": message,
    }
    try:
        response = requests.post(f"{BACKEND_URL}/api/chat", json=payload)
        response.raise_for_status()
    except Exception as e:
        st.error(f"Error: {e}")
        return
    data = response.json()
    st.session_state.conversation_id = data["conversation_id"]
    # Append the user message and bot reply to chat history
    st.session_state.chat_history.append(("user", message))
    st.session_state.chat_history.append(("assistant", data["reply"]))

# Use Streamlit's chat input (available in newer versions)
user_message = st.chat_input("Type your message here...")

if user_message:
    send_message(user_message)

# Display conversation history using chat message bubbles.
for role, message in st.session_state.chat_history:
    if role == "user":
        st.chat_message("user").write(message)
    else:
        st.chat_message("assistant").write(message)
