import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
import os
import json

# Try to load the API key from Render's secret file.
secret_file_path = "/etc/secrets/OPENAI_API_KEY"
if os.path.exists(secret_file_path):
    with open(secret_file_path, 'r') as file:
        openai.api_key = file.read().strip()
else:
    # Fallback: Load environment variables from .env for local development.
    from dotenv import load_dotenv
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Data structure for storing conversations.
# Each conversation contains: start_time, last_activity, and messages (a list of dicts with role, content, timestamp)
conversations: Dict[str, Dict[str, Any]] = {}

# Persona model – all fields are optional.
class Persona(BaseModel):
    background: Optional[str] = None
    tone: Optional[str] = None
    knowledge_domain: Optional[str] = None
    workflow: Optional[str] = None
    pain_points: Optional[str] = None
    sample_transcript: Optional[str] = None

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: str
    reply: str

def persist_logs():
    """Persist the conversations to a file for later insight."""
    with open("chat_logs.json", "w") as f:
        json.dump(conversations, f, indent=2)

# Global active persona (optional)
active_persona: Optional[Persona] = None

@app.get("/api/persona", response_model=Persona)
def get_persona():
    # Return the current persona (empty if not set)
    return active_persona or Persona()

@app.post("/api/persona", response_model=Persona)
def set_persona(persona: Persona):
    global active_persona
    active_persona = persona
    return active_persona

@app.post("/api/start", response_model=ChatResponse)
def start_conversation():
    global conversations, active_persona
    if active_persona is None:
        raise HTTPException(status_code=400, detail="No active persona configured.")
    
    now = datetime.utcnow().isoformat()
    conversation_id = str(uuid.uuid4())
    
    # Initialize a new conversation.
    conversations[conversation_id] = {
        "start_time": now,
        "last_activity": now,
        "messages": []
    }
    
    # Build the system prompt with persona details and instruct the assistant to greet the user.
    system_prompt = "You are a chatbot"
    if active_persona.background:
        system_prompt += f" with background: {active_persona.background}."
    if active_persona.tone:
        system_prompt += f" Tone: {active_persona.tone}."
    if active_persona.knowledge_domain:
        system_prompt += f" Knowledge Domain: {active_persona.knowledge_domain}."
    if active_persona.workflow:
        system_prompt += f" Workflow: {active_persona.workflow}."
    if active_persona.pain_points:
        system_prompt += f" Pain Points: {active_persona.pain_points}."
    if active_persona.sample_transcript:
        system_prompt += f" Sample Transcript: {active_persona.sample_transcript}."
    
    # Add instruction to greet the user first.
    system_prompt += " When starting a new conversation, greet the user based on your persona."
    
    # Provide an empty user message to trigger the greeting.
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": ""}
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    reply = response.choices[0].message.content.strip()
    
    # Log the assistant's greeting.
    conversations[conversation_id]["messages"].append({
        "role": "assistant",
        "content": reply,
        "timestamp": now
    })
    
    # Persist the conversation logs.
    persist_logs()
    
    return ChatResponse(conversation_id=conversation_id, reply=reply)

@app.post("/api/chat", response_model=ChatResponse)
def chat(chat_req: ChatRequest):
    global conversations, active_persona
    if active_persona is None:
        raise HTTPException(status_code=400, detail="No active persona configured.")
    
    now = datetime.utcnow().isoformat()
    conversation_id = chat_req.conversation_id or str(uuid.uuid4())
    
    # Initialize conversation if it doesn't exist.
    if conversation_id not in conversations:
        conversations[conversation_id] = {
            "start_time": now,
            "last_activity": now,
            "messages": []
        }
    else:
        conversations[conversation_id]["last_activity"] = now

    # Build the system prompt based on available persona fields.
    system_prompt = "You are a chatbot"
    if active_persona.background:
        system_prompt += f" with background: {active_persona.background}."
    if active_persona.tone:
        system_prompt += f" Tone: {active_persona.tone}."
    if active_persona.knowledge_domain:
        system_prompt += f" Knowledge Domain: {active_persona.knowledge_domain}."
    if active_persona.workflow:
        system_prompt += f" Workflow: {active_persona.workflow}."
    if active_persona.pain_points:
        system_prompt += f" Pain Points: {active_persona.pain_points}."
    if active_persona.sample_transcript:
        system_prompt += f" Sample Transcript: {active_persona.sample_transcript}."

    # Build messages list: system prompt, prior messages, then new user message.
    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversations[conversation_id]["messages"]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": chat_req.message})
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    reply = response.choices[0].message.content.strip()
    
    # Log the new messages with a timestamp.
    conversations[conversation_id]["messages"].append({
        "role": "user",
        "content": chat_req.message,
        "timestamp": now
    })
    conversations[conversation_id]["messages"].append({
        "role": "assistant",
        "content": reply,
        "timestamp": now
    })
    
    # Persist logs to a file.
    persist_logs()
    
    return ChatResponse(conversation_id=conversation_id, reply=reply)

@app.get("/api/logs")
def get_logs():
    """Return all conversation logs along with metadata."""
    return conversations

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
