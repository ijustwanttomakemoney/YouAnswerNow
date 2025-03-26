# chat_streamlit.py
import streamlit as st
import requests
from PIL import Image

# Update BACKEND_URL with your deployed backend URL.
BACKEND_URL = "https://youanswernow.onrender.com"

image = Image.open("YAN_LOGO.png")
st.image(image, width=300)

# Initialize session state for conversation details.
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
    st.session_state.chat_history.append(("user", message))
    st.session_state.chat_history.append(("assistant", data["reply"]))

# Use Streamlit's chat input (requires a recent version of Streamlit)
user_message = st.chat_input("Type your message here...")

if user_message:
    send_message(user_message)

# Display conversation history using chat bubbles.
for role, message in st.session_state.chat_history:
    if role == "user":
        st.chat_message("user").write(message)
    else:
        st.chat_message("assistant").write(message)
