# backend/ollama_keepalive.py
"""
Background thread to keep Ollama connection alive and model loaded.
Prevents ECONNRESET errors by pinging Ollama periodically.
"""

import threading
import time
import requests
import logging
from config import OLLAMA_HOST, OLLAMA_PORT, MODEL_NAME

logger = logging.getLogger(__name__)

class OllamaKeepAlive:
    def __init__(self, ping_interval: int = 120):  # Ping every 2 minutes
        self.ping_interval = ping_interval
        self.api_url = f"{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"
        self.running = False
        self.thread = None

    def start(self):
        """Start the keep-alive background thread."""
        if self.running:
            logger.warning("Keep-alive thread already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._keep_alive_loop, daemon=True)
        self.thread.start()
        logger.info(f"Started Ollama keep-alive thread (ping every {self.ping_interval}s)")

    def stop(self):
        """Stop the keep-alive thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Stopped Ollama keep-alive thread")

    def _keep_alive_loop(self):
        """Background loop that pings Ollama to keep connection alive."""
        # Import lock from llm_handler to sync with user queries
        try:
            from llm_handler import _ollama_lock
        except ImportError:
            logger.warning("Could not import _ollama_lock, keep-alive will run without sync")
            _ollama_lock = None

        # Wait before first ping to let system initialize
        time.sleep(30)

        while self.running:
            try:
                # Send a minimal request to keep model loaded
                payload = {
                    "model": MODEL_NAME,
                    "prompt": "ping",  # Minimal prompt
                    "stream": False,
                    "keep_alive": "5m",
                    "options": {
                        "num_predict": 1,  # Only generate 1 token
                        "temperature": 0.0
                    }
                }

                logger.debug(f"Sending keep-alive ping to Ollama...")

                # Use lock if available to prevent conflicts with user queries
                if _ollama_lock:
                    with _ollama_lock:
                        r = requests.post(self.api_url, json=payload, timeout=30)
                else:
                    r = requests.post(self.api_url, json=payload, timeout=30)

                if r.status_code == 200:
                    logger.debug("Keep-alive ping successful")
                else:
                    logger.warning(f"Keep-alive ping returned status {r.status_code}")

            except Exception as e:
                logger.warning(f"Keep-alive ping failed: {e}")

            # Wait before next ping
            time.sleep(self.ping_interval)

    def ping_once(self):
        """Manually trigger a single ping (useful before queries)."""
        try:
            payload = {
                "model": MODEL_NAME,
                "prompt": "ping",
                "stream": False,
                "keep_alive": "5m",
                "options": {
                    "num_predict": 1,
                    "temperature": 0.0
                }
            }
            r = requests.post(self.api_url, json=payload, timeout=10)
            return r.status_code == 200
        except Exception as e:
            logger.debug(f"Manual ping failed: {e}")
            return False

# Global instance
keep_alive = OllamaKeepAlive(ping_interval=120)
