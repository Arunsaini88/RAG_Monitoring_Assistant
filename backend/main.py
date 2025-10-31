# backend/main.py

import uvicorn
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import sys
import os
from collections import defaultdict
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from embeddings_engine import EmbeddingEngine
from llm_handler import query_llm
from prompt_templates import build_prompt
from config import HOST, PORT, TOP_K, DATA_PATH, EMBEDDING_MODEL, OLLAMA_HOST, OLLAMA_PORT
# from ollama_keepalive import keep_alive  # Disabled - caused race conditions

app = FastAPI(title="Offline RAG Prototype")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize embedding engine (auto-refresh thread starts inside)
engine = EmbeddingEngine()

# Conversation history storage (session_id -> list of {role, content, timestamp})
conversation_history = defaultdict(list)
MAX_HISTORY_LENGTH = 10  # Keep last 10 exchanges (5 Q&A pairs)
SESSION_TIMEOUT = timedelta(hours=1)  # Clear history after 1 hour of inactivity

# Keep-alive disabled - was causing race conditions with user queries
# The lock in llm_handler.py now prevents concurrent requests
# keep_alive.start()

def clean_old_sessions():
    """Remove conversation history for sessions that haven't been active recently."""
    now = datetime.now()
    sessions_to_remove = []
    for session_id, history in conversation_history.items():
        if history:
            last_timestamp = history[-1].get('timestamp', now)
            if now - last_timestamp > SESSION_TIMEOUT:
                sessions_to_remove.append(session_id)
    for session_id in sessions_to_remove:
        del conversation_history[session_id]

def add_to_history(session_id: str, role: str, content: str):
    """Add a message to conversation history."""
    clean_old_sessions()
    conversation_history[session_id].append({
        'role': role,
        'content': content,
        'timestamp': datetime.now()
    })
    # Keep only recent history
    if len(conversation_history[session_id]) > MAX_HISTORY_LENGTH:
        conversation_history[session_id] = conversation_history[session_id][-MAX_HISTORY_LENGTH:]

def get_conversation_context(session_id: str) -> List[Dict]:
    """Get conversation history for a session."""
    return conversation_history.get(session_id, [])

@app.get("/")
def root():
    return {"status": "running", "indexed_records": len(engine.metadata)}

@app.get("/health")
def health_check():
    """Health check endpoint to verify system status."""
    return {
        "status": "healthy",
        "indexed_records": len(engine.metadata),
        "index_initialized": engine.index is not None,
        "embedding_model": EMBEDDING_MODEL,
        "ollama_endpoint": f"{OLLAMA_HOST}:{OLLAMA_PORT}"
    }

@app.post("/update_data")
def update_data(data: List[Dict] = Body(...)):
    if not isinstance(data, list):
        return {"error": "expected list of records"}
    count = engine.add_records(data)
    return {"message": f"Indexed {count} records (total)."}

@app.post("/refresh")
def refresh_data():
    """Reload data from source and rebuild index if changed."""
    import time
    start_time = time.time()
    count = engine.refresh_from_source()
    elapsed = time.time() - start_time
    return {
        "message": f"Refresh completed in {elapsed:.1f}s",
        "indexed_records": count,
        "data_changed": elapsed > 1.0  # If took more than 1s, probably rebuilt
    }

@app.post("/query")
def query_endpoint(body: Dict = Body(...)):
    # Accept either {"query": "..."} or raw string in "query"
    question = body.get("query") if isinstance(body, dict) else None
    session_id = body.get("session_id", "default")  # Use session_id from client or default

    if not question or not question.strip():
        return {"error": "please send {'query': '<your question>'}"}

    # Get conversation history for context
    conversation_context = get_conversation_context(session_id)

    # Retrieve top-k relevant records
    context_records = engine.query(question, k=TOP_K)

    # Build prompt with conversation history
    prompt = build_prompt(question, context_records, conversation_context)

    # Get LLM response
    llm_response = query_llm(prompt)

    # Store this exchange in conversation history
    add_to_history(session_id, "user", question)
    add_to_history(session_id, "assistant", llm_response)

    return {
        "answer": llm_response,
        "context_count": len(context_records),
        "top_context": context_records,
        "conversation_length": len(conversation_history[session_id])
    }

@app.post("/clear_history")
def clear_history(body: Dict = Body(...)):
    """Clear conversation history for a session."""
    session_id = body.get("session_id", "default")
    if session_id in conversation_history:
        del conversation_history[session_id]
        return {"message": f"Conversation history cleared for session {session_id}"}
    return {"message": "No history found for this session"}

if __name__ == "__main__":
    # ensure data file exists
    data_file_path = os.path.join(os.path.dirname(__file__), DATA_PATH)
    if not os.path.exists(data_file_path):
        with open(data_file_path, "w") as f:
            f.write("[]")
        print(f"Created empty data file: {data_file_path}")
    uvicorn.run(app, host=HOST, port=PORT)
