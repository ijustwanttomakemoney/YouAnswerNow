# admin_streamlit.py
import streamlit as st
import requests

BACKEND_URL = "https://youanswernow.onrender.com"  # Update as needed

st.title("Admin - Configure Chatbot Persona")

st.markdown("Fill in the details below to update the active persona:")

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
        response = requests.post(f"{BACKEND_URL}/api/persona", json=payload)
        if response.ok:
            st.success("Persona updated successfully!")
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
