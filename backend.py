# backend.py
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import uuid
from typing import Optional, List, Dict
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from your .env file or Render secret file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# In-memory storage for the active persona and conversation logs.
active_persona = None  # Set via the /api/persona endpoint.
# Conversations: dict mapping conversation_id to a list of messages.
# Each message is a dict: { "role": <str>, "content": <str>, "timestamp": <str> }
conversations: Dict[str, List[Dict[str, str]]] = {}

# Pydantic models for request/response payloads.
class Persona(BaseModel):
    background: str
    tone: str
    knowledge_domain: str
    workflow: str
    pain_points: str
    sample_transcript: Optional[str] = None

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: str
    reply: str

@app.get("/api/persona", response_model=Persona)
def get_persona():
    if active_persona is None:
        raise HTTPException(status_code=404, detail="No active persona set.")
    return active_persona

@app.post("/api/persona", response_model=Persona)
def set_persona(persona: Persona):
    global active_persona
    active_persona = persona
    return active_persona

@app.post("/api/chat", response_model=ChatResponse)
def chat(chat_req: ChatRequest):
    global conversations, active_persona
    if active_persona is None:
        raise HTTPException(status_code=400, detail="No active persona configured.")
    
    # Create or retrieve conversation_id.
    conversation_id = chat_req.conversation_id or str(uuid.uuid4())
    if conversation_id not in conversations:
        conversations[conversation_id] = []
    
    # Build the system prompt from the active persona.
    system_prompt = (
        f"You are a chatbot with the following persona:\n"
        f"Background: {active_persona.background}\n"
        f"Tone: {active_persona.tone}\n"
        f"Knowledge Domain: {active_persona.knowledge_domain}\n"
        f"Workflow: {active_persona.workflow}\n"
        f"Pain Points: {active_persona.pain_points}\n"
    )
    if active_persona.sample_transcript:
        system_prompt += f"Sample Transcript: {active_persona.sample_transcript}\n"
    
    # Build the messages for the conversation.
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversations[conversation_id])
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
    now = datetime.utcnow().isoformat()
    
    # Log the user's message and the assistant's reply with a timestamp.
    conversations[conversation_id].append({
        "role": "user",
        "content": chat_req.message,
        "timestamp": now
    })
    conversations[conversation_id].append({
        "role": "assistant",
        "content": reply,
        "timestamp": now
    })
    
    return ChatResponse(conversation_id=conversation_id, reply=reply)

@app.get("/api/logs")
def get_logs():
    # Returns all conversation logs.
    return conversations

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
