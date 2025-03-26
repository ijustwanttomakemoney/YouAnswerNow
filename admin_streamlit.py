# admin_streamlit.py
import streamlit as st
import requests
import pandas as pd

# Set your backend URL (update accordingly)
BACKEND_URL = "https://youanswernow.onrender.com"

st.title("Admin - Configure Chatbot Persona & Real-Time Logs")

st.header("Persona Configuration")
with st.form("persona_form", clear_on_submit=True):
    background = st.text_area("Background", placeholder="Describe the persona's background")
    tone = st.text_input("Tone", placeholder="Enter the desired tone")
    knowledge_domain = st.text_input("Knowledge Domain", placeholder="e.g. Technology, Marketing")
    workflow = st.text_area("Workflow", placeholder="Describe the conversational workflow")
    pain_points = st.text_area("Pain Points", placeholder="List any pain points or needs")
    sample_transcript = st.text_area("Sample Transcript (optional)", placeholder="Enter sample Q&A if any")
    
    submitted = st.form_submit_button("Save Persona")
    
    if submitted:
        payload = {
            "background": background,
            "tone": tone,
            "knowledge_domain": knowledge_domain,
            "workflow": workflow,
            "pain_points": pain_points,
            "sample_transcript": sample_transcript,
        }
        try:
            response = requests.post(f"{BACKEND_URL}/api/persona", json=payload)
            response.raise_for_status()
            st.success("Persona updated successfully!")
        except Exception as e:
            st.error(f"Error: {e}")

st.header("Real-Time Chat Logs")
# Auto-refresh the dashboard every 5 seconds.
_ = st.experimental_autorefresh(interval=5000, limit=100, key="admin_autorefresh")

try:
    response = requests.get(f"{BACKEND_URL}/api/logs")
    response.raise_for_status()
    logs_data = response.json()
    # Flatten the logs: each conversation becomes multiple rows.
    flat_logs = []
    for conv_id, messages in logs_data.items():
        for msg in messages:
            flat_logs.append({
                "Conversation ID": conv_id,
                "Role": msg.get("role"),
                "Content": msg.get("content"),
                "Timestamp": msg.get("timestamp")
            })
    if flat_logs:
        df = pd.DataFrame(flat_logs)
        st.dataframe(df)
    else:
        st.info("No logs available yet.")
except Exception as e:
    st.error(f"Error fetching logs: {e}")
