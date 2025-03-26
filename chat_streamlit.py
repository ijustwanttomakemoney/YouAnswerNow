# chat_streamlit.py
import streamlit as st
import requests

# Set your backend URL – for local testing, you might use "http://localhost:8000"
# In production, replace this with the actual URL where your backend is hosted.
BACKEND_URL = "http://localhost:8000"

st.title("Chat with the Persona-Based Bot")

# Use Streamlit session_state to persist the conversation_id and chat history
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def send_message(message):
    payload = {
        "conversation_id": st.session_state.conversation_id,
        "message": message,
    }
    response = requests.post(f"{https://youanswernow.onrender.com}/api/chat", json=payload)
    if response.ok:
        data = response.json()
        st.session_state.conversation_id = data["conversation_id"]
        # Append user message and bot reply to chat history
        st.session_state.chat_history.append(("USER", message))
        st.session_state.chat_history.append(("BOT", data["reply"]))
    else:
        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

with st.form("chat_form", clear_on_submit=True):
    user_message = st.text_input("Your Message")
    submitted = st.form_submit_button("Send")
    if submitted and user_message:
        send_message(user_message)

st.markdown("### Conversation:")
for sender, message in st.session_state.chat_history:
    if sender == "USER":
        st.markdown(f"**You:** {message}")
    else:
        st.markdown(f"**Bot:** {message}")
