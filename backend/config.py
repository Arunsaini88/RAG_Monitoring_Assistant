# backend/config.py

# Data source
DATA_SOURCE_TYPE = "json"   # "json" or "api"
DATA_PATH = "data.json"     # local JSON path (backend folder)
API_URL = "http://localhost:5000/api/data"  # if using API source

# Refresh interval (seconds)
REFRESH_INTERVAL = 1800  # 30 minutes

# FAISS / embedding storage
EMBEDDING_INDEX_PATH = "./faiss_index.index"
METADATA_STORE_PATH = "./metadata_store.json"
DATA_HASH_PATH = "./data_hash.txt"  # Store hash of data to detect changes

# Embedding model (paraphrase-MiniLM-L3-v2 is 2x faster, slightly lower quality but good enough)
EMBEDDING_MODEL = "paraphrase-MiniLM-L3-v2"  # Faster alternative: "all-MiniLM-L6-v2"

# Performance settings
LAZY_LOAD = True  # If True, skip initial indexing on startup (index on first query)
BATCH_SIZE = 128  # Larger batch size for faster embedding generation
NUM_WORKERS = 4  # Number of parallel workers for encoding

# Ollama / local LLM settings
OLLAMA_HOST = "http://127.0.0.1"  # Include protocol (http:// or https://)
OLLAMA_PORT = 11434
MODEL_NAME = "llama3.2:1b"   # llama3.2:1b is MUCH better than tinyllama (same size, less hallucination!)

# FastAPI server config
HOST = "0.0.0.0"
PORT = 8000

# Retriever params (reduced from 6 to 4 for faster LLM processing)
TOP_K = 4
