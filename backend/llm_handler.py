# backend/llm_handler.py

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import logging
import time
from typing import Optional
from config import OLLAMA_HOST, OLLAMA_PORT, MODEL_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_API = f"{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"

# Create a lock to prevent concurrent Ollama requests (Windows Ollama bug)
import threading
_ollama_lock = threading.Lock()

# Create a session with connection pooling and keep-alive
def create_session():
    """Create a requests session with proper retry and connection handling."""
    session = requests.Session()

    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"]
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=1,
        pool_maxsize=1,
        pool_block=False
    )

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Set default headers
    session.headers.update({
        'Connection': 'keep-alive',
        'Content-Type': 'application/json'
    })

    return session

# Global session (reused across requests)
_session = create_session()

# Simple in-memory cache for responses (LRU-style with max 100 entries)
_response_cache = {}
_cache_max_size = 100

def _get_cache_key(prompt: str) -> str:
    """Generate a cache key from the prompt."""
    import hashlib
    return hashlib.md5(prompt.encode()).hexdigest()

def _get_cached_response(prompt: str) -> Optional[str]:
    """Get cached response if available."""
    key = _get_cache_key(prompt)
    if key in _response_cache:
        logger.info("Cache hit! Returning cached response")
        return _response_cache[key]
    return None

def _cache_response(prompt: str, response: str):
    """Cache a response with LRU eviction."""
    global _response_cache
    key = _get_cache_key(prompt)

    # Simple LRU: if cache is full, remove oldest (first) entry
    if len(_response_cache) >= _cache_max_size:
        _response_cache.pop(next(iter(_response_cache)))

    _response_cache[key] = response

def query_llm(prompt: str, max_tokens: int = 100, temperature: float = 0.7, retry_count: int = 5) -> str:
    """
    Calls Ollama local HTTP API to generate a completion.
    Uses the correct Ollama API format with proper parameter names.

    Args:
        prompt: The prompt to send to the LLM
        max_tokens: Maximum number of tokens to generate (mapped to num_predict)
        temperature: Temperature for generation (0.0 = deterministic)
        retry_count: Number of retry attempts (increased to 5 for better reliability)

    Returns:
        The generated text response from the LLM
    """
    global _session  # Declare at the beginning of function

    # Check cache first for instant responses
    cached = _get_cached_response(prompt)
    if cached:
        return cached

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,  # Get complete response at once
        "keep_alive": "10m",  # Keep model loaded for 10 minutes (prevents unload/reload)
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
            "num_ctx": 1024,  # Reduced context window for faster processing (from default 2048)
            "top_k": 20,  # Faster sampling
            "top_p": 0.9,  # Nucleus sampling for speed
        }
    }

    # Retry logic for connection issues
    for attempt in range(retry_count):
        response = None
        try:
            # Acquire lock to prevent concurrent requests (Ollama Windows bug)
            with _ollama_lock:
                logger.info(f"Sending request to Ollama API (attempt {attempt + 1}/{retry_count})")

                # Use persistent session with connection pooling
                response = _session.post(
                    OLLAMA_API,
                    json=payload,
                    timeout=180,
                    stream=False
                )
                response.raise_for_status()

                # Parse the response INSIDE the lock to avoid connection issues
                data = response.json()

                # Ollama returns {"response": "...", "done": true, ...}
                if isinstance(data, dict) and "response" in data:
                    response_text = data["response"].strip()
                    if response_text:
                        logger.info(f"Successfully received response from Ollama")
                        # Cache the successful response
                        _cache_response(prompt, response_text)
                        return response_text
                    else:
                        logger.warning("Received empty response from Ollama")
                        return "[Empty response from LLM]"

                # Fallback for unexpected response format
                logger.warning(f"Unexpected Ollama response format: {data}")
                return f"[Unexpected response format] {json.dumps(data)}"

        except (requests.exceptions.ConnectionError, ConnectionResetError, requests.exceptions.ChunkedEncodingError) as e:
            logger.warning(f"Connection error on attempt {attempt + 1}: {type(e).__name__}: {str(e)}")
            if attempt < retry_count - 1:
                wait_time = 1 + (attempt * 1)  # Backoff: 1s, 2s, 3s, 4s, 5s
                logger.info(f"Auto-retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                # Recreate session on connection error
                _session = create_session()
                continue
            else:
                error_msg = f"Connection to Ollama failed after {retry_count} attempts. Make sure Ollama is running."
                logger.error(error_msg)
                return f"[LLM Connection Error] {error_msg}"

        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout on attempt {attempt + 1}")
            if attempt < retry_count - 1:
                logger.info(f"Retrying after timeout...")
                time.sleep(2)
                continue
            else:
                error_msg = "Request to Ollama timed out after multiple attempts."
                logger.error(error_msg)
                return f"[LLM Timeout Error] {error_msg}"

        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error from Ollama: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return f"[LLM HTTP Error] {error_msg}"

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            if attempt < retry_count - 1:
                logger.info(f"Retrying after JSON decode error...")
                time.sleep(1)
                continue
            return f"[LLM Error] Invalid JSON response from Ollama"

        except Exception as e:
            logger.error(f"Unexpected error querying LLM: {type(e).__name__}: {e}")
            if attempt < retry_count - 1:
                time.sleep(1)
                continue
            return f"[LLM Error] {type(e).__name__}: {e}"

        finally:
            # Ensure response is closed properly
            if response is not None:
                response.close()

    return "[LLM Error] Max retries exceeded"
