# Offline RAG System for License Monitoring

A high-performance Retrieval-Augmented Generation (RAG) system for querying and analyzing software license usage data using local LLMs via Ollama. Features conversational AI with context awareness, optimized for fast CPU-based inference.

## Features

- **Offline-First Architecture**: Runs entirely locally with no external API dependencies
- **Fast RAG Pipeline**: Optimized for 8-12 second response times on CPU
- **Conversational AI**: Maintains conversation history and context across questions
- **Real-time Data Indexing**: FAISS-based vector search with automatic index caching
- **Smart Caching**: LRU cache for instant responses to repeated queries (<0.1s)
- **Interactive CLI**: User-friendly command-line interface with debug mode
- **Auto-Refresh**: Background data monitoring with intelligent cache invalidation

## Architecture

### Backend (FastAPI + Python)
- **FastAPI REST API** with CORS support
- **FAISS** vector database for semantic search
- **Sentence Transformers** for embeddings (`paraphrase-MiniLM-L3-v2`)
- **Ollama** integration for local LLM inference (`llama3.2:1b`)
- Session-based conversation history management

### Frontend (Node.js CLI)
- Interactive command-line interface
- Session management and conversation tracking
- Debug mode for inspecting retrieved context
- Health monitoring and data refresh commands

## Prerequisites

1. **Python 3.8+** with pip
2. **Node.js 16+** with npm
3. **Ollama** installed and running ([Download here](https://ollama.ai))
4. **Llama 3.2:1b model** pulled in Ollama

## Installation

### 1. Install Ollama and Pull Model

```bash
# Install Ollama (visit https://ollama.ai for your OS)

# Pull the Llama 3.2:1b model
ollama pull llama3.2:1b
```

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Backend Dependencies:**
- fastapi
- uvicorn[standard]
- sentence-transformers
- faiss-cpu
- requests
- numpy
- python-multipart

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

**Frontend Dependencies:**
- axios
- readline-sync

## Quick Start

### Option 1: Use the Launcher (Windows)

Simply double-click [start_offline_rag.bat](start_offline_rag.bat) to launch all services:
- Starts Ollama server
- Starts FastAPI backend on port 8000
- Starts Node.js CLI frontend

### Option 2: Manual Start

**Terminal 1 - Start Ollama:**
```bash
ollama serve
```

**Terminal 2 - Start Backend:**
```bash
cd backend
python main.py
```

**Terminal 3 - Start Frontend:**
```bash
cd frontend
node app.js
```

## Usage

### CLI Commands

Once the frontend is running, you can use these commands:

```
Ask question> which software has the highest usage?
Ask question> show me MATLAB licenses in USA
Ask question> health      # Check system status
Ask question> refresh     # Reload data from source
Ask question> debug       # Toggle detailed context display
Ask question> clear       # Clear conversation history
Ask question> exit        # Quit the application
```

### API Endpoints

**Health Check:**
```bash
GET http://localhost:8000/health
```

**Query with RAG:**
```bash
POST http://localhost:8000/query
Content-Type: application/json

{
  "query": "which software has highest usage?",
  "session_id": "optional-session-id"
}
```

**Refresh Data:**
```bash
POST http://localhost:8000/refresh
```

**Clear Conversation History:**
```bash
POST http://localhost:8000/clear_history
Content-Type: application/json

{
  "session_id": "session-id-to-clear"
}
```

## Configuration

### Backend Configuration

Edit [backend/config.py](backend/config.py) to customize:

```python
# Data source
DATA_PATH = "data.json"              # Path to license data
REFRESH_INTERVAL = 1800              # Auto-refresh interval (seconds)

# Embedding model
EMBEDDING_MODEL = "paraphrase-MiniLM-L3-v2"

# LLM settings
MODEL_NAME = "llama3.2:1b"
OLLAMA_HOST = "http://127.0.0.1"
OLLAMA_PORT = 11434

# RAG parameters
TOP_K = 4                             # Number of context records to retrieve
```

### Performance Tuning

See [SPEED_OPTIMIZATIONS.md](SPEED_OPTIMIZATIONS.md) for detailed performance tuning options.

**Key optimizations applied:**
- Token reduction (max_tokens=100) for 40% faster responses
- Context window reduction (num_ctx=1024) for 20% faster inference
- Fast embedding model (L3 instead of L6) for 2x faster embeddings
- LRU caching for instant repeated queries
- Optimized sampling parameters (top_k, top_p)

## Data Format

The system expects license data in JSON format at [backend/data.json](backend/data.json):

```json
[
  {
    "software": "Autodesk",
    "server": "27000@SRV00001",
    "location": "USA",
    "license": "98765ACAD_E_2023_0F",
    "latest_license_issued": 45,
    "license_day_peak": 8,
    "license_day_average": 5,
    "license_work_peak": 7,
    "license_work_average": 4,
    "percentage_work_peak": 85,
    "percentage_work_average": 60
  }
]
```

### Generate Sample Data

Run [data.py](data.py) to generate 10,000 sample records:

```bash
python data.py
```

This creates `license_data_sample.json` with randomized license data for testing.

## Performance

### Response Times (CPU)

| Query Type | Expected Time | Notes |
|------------|--------------|-------|
| First-time query | 8-12s | Full LLM generation |
| Repeated query | <0.1s | Served from cache |
| Conversational follow-up | 8-12s | Different context |

### Hardware Requirements

| Hardware | Response Time | Recommended |
|----------|--------------|-------------|
| Modern CPU (i5/i7) | 8-12s | Acceptable |
| Apple Silicon (M1/M2) | 3-5s | Great |
| GPU (RTX 3060+) | 1-2s | Excellent |

### Performance Monitoring

The CLI displays timing information for each query:

```
Response time: 9.2s | Used 4 records | 2 msgs in history
```

## Project Structure

```
First_RAG/
├── backend/
│   ├── main.py                  # FastAPI application
│   ├── config.py                # Configuration settings
│   ├── embeddings_engine.py     # FAISS indexing and search
│   ├── llm_handler.py           # Ollama LLM integration
│   ├── prompt_templates.py      # Prompt engineering
│   ├── ollama_keepalive.py      # Keep-alive utility (disabled)
│   ├── data.json                # License data (10K records)
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── app.js                   # CLI interface
│   ├── package.json             # Node.js dependencies
│   └── package-lock.json
├── data.py                      # Sample data generator
├── start_offline_rag.bat        # Windows launcher
├── SPEED_OPTIMIZATIONS.md       # Performance tuning guide
└── README.md                    # This file
```

## Troubleshooting

### Issue: Slow First Query (2-3 minutes)

**Cause:** Building FAISS index on first run

**Solution:** Wait for index to build. Subsequent queries will be fast. The index is cached for future runs.

### Issue: Connection Refused

**Cause:** Backend or Ollama not running

**Solution:**
1. Check if Ollama is running: `ollama serve`
2. Check if backend is running: `curl http://localhost:8000/health`
3. Ensure ports 8000 and 11434 are not in use

### Issue: Model Not Found

**Cause:** Llama 3.2:1b model not pulled

**Solution:**
```bash
ollama pull llama3.2:1b
```

### Issue: Out of Memory

**Cause:** Large dataset or insufficient RAM

**Solution:**
- Reduce `BATCH_SIZE` in [backend/config.py](backend/config.py)
- Use smaller embedding model
- Process data in smaller chunks

### Issue: Slow Responses (>15s)

**Cause:** System under load or suboptimal settings

**Solution:**
1. Check CPU usage during query
2. Reduce `max_tokens` in [backend/llm_handler.py](backend/llm_handler.py)
3. Decrease `TOP_K` in [backend/config.py](backend/config.py)
4. Review [SPEED_OPTIMIZATIONS.md](SPEED_OPTIMIZATIONS.md)

## Advanced Features

### Conversation History

The system maintains conversation context across queries within a session:

```
Ask question> show me MATLAB licenses
AI Assistant: MATLAB has 42 licenses with an average usage of 65%

Ask question> what about in the USA specifically?
AI Assistant: In the USA, MATLAB has 18 licenses with 70% usage
```

### Auto-Refresh

The backend monitors [backend/data.json](backend/data.json) and automatically refreshes the index when data changes (configurable interval: 30 minutes).

### Debug Mode

Enable debug mode to see retrieved context and embeddings:

```
Ask question> debug
Debug mode: ON

Ask question> show me Autodesk licenses
[Shows full context records, embeddings, and retrieval scores]
```

## Development

### Adding New Data Sources

1. Update [backend/config.py](backend/config.py) to point to your data
2. Ensure data follows the expected JSON schema
3. Restart backend to rebuild index

### Customizing Prompts

Edit [backend/prompt_templates.py](backend/prompt_templates.py) to adjust:
- System instructions
- Context formatting
- Conversation history integration

### Changing LLM Model

1. Pull desired model: `ollama pull <model-name>`
2. Update `MODEL_NAME` in [backend/config.py](backend/config.py)
3. Restart backend

**Recommended models:**
- `llama3.2:1b` - Best balance (current)
- `llama3.2:3b` - Better quality, slower
- `phi3:mini` - Alternative small model

## License

This project is provided as-is for educational and internal use.

## Contributing

To contribute or report issues:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with detailed description

## Support

For questions or issues:
- Review [SPEED_OPTIMIZATIONS.md](SPEED_OPTIMIZATIONS.md) for performance tuning
- Check system logs in backend terminal
- Verify Ollama service status: `ollama list`

---

**Built with:** FastAPI | FAISS | Sentence Transformers | Ollama | Node.js
