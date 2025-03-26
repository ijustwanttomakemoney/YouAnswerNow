# admin_streamlit.py
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Update BACKEND_URL with your deployed backend URL.
BACKEND_URL = "https://youanswernow.onrender.com"

st.title("Admin - Configure Chatbot Persona & Real-Time Logs")

st.header("Persona Configuration")
with st.form("persona_form", clear_on_submit=True):
    background = st.text_area("Background (optional)", placeholder="Describe the persona's background")
    tone = st.text_input("Tone (optional)", placeholder="Enter the desired tone")
    knowledge_domain = st.text_input("Knowledge Domain (optional)", placeholder="e.g. Technology, Marketing")
    workflow = st.text_area("Workflow (optional)", placeholder="Describe the conversational workflow")
    pain_points = st.text_area("Pain Points (optional)", placeholder="List any pain points or needs")
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

st.header("Real-Time Chat Logs & Metrics")

# Auto-refresh the dashboard every 5 seconds.
st_autorefresh(interval=5000, limit=100, key="admin_autorefresh")

try:
    response = requests.get(f"{BACKEND_URL}/api/logs")
    response.raise_for_status()
    logs_data = response.json()
    
    # Compute metrics: number of active conversations (users) and average session duration.
    num_users = len(logs_data)
    durations = []
    flat_logs = []
    for conv_id, conv in logs_data.items():
        start_time = datetime.fromisoformat(conv.get("start_time"))
        last_activity = datetime.fromisoformat(conv.get("last_activity"))
        duration = (last_activity - start_time).total_seconds()
        durations.append(duration)
        for msg in conv.get("messages", []):
            flat_logs.append({
                "Conversation ID": conv_id,
                "Role": msg.get("role"),
                "Content": msg.get("content"),
                "Timestamp": msg.get("timestamp")
            })
    
    avg_duration = sum(durations)/len(durations) if durations else 0
    
    st.metric("Active Users", num_users)
    st.metric("Avg Session Duration (sec)", round(avg_duration, 2))
    
    if flat_logs:
        df = pd.DataFrame(flat_logs)
        st.dataframe(df)
    else:
        st.info("No logs available yet.")
except Exception as e:
    st.error(f"Error fetching logs: {e}")
