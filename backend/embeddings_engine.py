# backend/embeddings_engine.py

import os
import json
import time
import threading
import logging
import hashlib
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from config import (
    DATA_SOURCE_TYPE, DATA_PATH, API_URL,
    EMBEDDING_INDEX_PATH, METADATA_STORE_PATH, DATA_HASH_PATH,
    EMBEDDING_MODEL, REFRESH_INTERVAL, LAZY_LOAD, BATCH_SIZE, NUM_WORKERS
)
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingEngine:
    def __init__(self):
        logger.info("Initializing EmbeddingEngine...")

        # Load model with optimized settings
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        self.model = SentenceTransformer(EMBEDDING_MODEL)

        # Set number of workers for parallel encoding
        self.model.encode = self._wrap_encode(self.model.encode)

        self.index = None
        self.metadata = []  # list of records in same order as vectors
        self._initialized = False
        self._lock = threading.Lock()  # For thread-safe operations

        # Try to load existing index/metadata
        if os.path.exists(EMBEDDING_INDEX_PATH) and os.path.exists(METADATA_STORE_PATH):
            try:
                logger.info("Loading existing index from disk...")
                self.index = faiss.read_index(EMBEDDING_INDEX_PATH)
                with open(METADATA_STORE_PATH, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                logger.info(f"✓ Loaded existing index ({len(self.metadata)} items) in seconds!")
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to load existing index: {e}")
                self.index = None
                self.metadata = []

        # Try initial load if no existing index and LAZY_LOAD is disabled
        if not self._initialized and not LAZY_LOAD:
            logger.info("No existing index found. Building index from data source...")
            try:
                count = self.refresh_from_source()
                if count > 0:
                    self._initialized = True
                    logger.info(f"✓ Initial index built with {count} records.")
                else:
                    logger.warning("No data available for initial indexing.")
            except Exception as e:
                logger.error(f"Initial data load failed: {e}")
        elif not self._initialized and LAZY_LOAD:
            logger.info("⚡ LAZY_LOAD enabled - skipping initial indexing. Will index on first query.")

        # Start auto refresh thread
        threading.Thread(target=self._auto_refresh_loop, daemon=True).start()
        logger.info("Auto-refresh thread started.")

    def _wrap_encode(self, original_encode):
        """Wrapper to add default parameters for faster encoding."""
        def encode_wrapper(sentences, **kwargs):
            # Set optimal defaults if not specified
            kwargs.setdefault('batch_size', BATCH_SIZE)
            kwargs.setdefault('show_progress_bar', True)
            kwargs.setdefault('convert_to_numpy', True)
            # Note: num_workers is not supported in newer versions of sentence-transformers
            # Removed to avoid compatibility issues
            return original_encode(sentences, **kwargs)
        return encode_wrapper

    def _load_records(self) -> List[Dict]:
        """Load records from configured data source."""
        if DATA_SOURCE_TYPE == "json":
            if not os.path.exists(DATA_PATH):
                logger.warning(f"Data file not found: {DATA_PATH}")
                return []
            try:
                with open(DATA_PATH, "r", encoding="utf-8") as f:
                    records = json.load(f)
                if not isinstance(records, list):
                    logger.error(f"Data file must contain a JSON array, got: {type(records)}")
                    return []
                logger.info(f"Loaded {len(records)} records from {DATA_PATH}")
                return records
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in data file: {e}")
                return []
            except Exception as e:
                logger.error(f"Error reading data file: {e}")
                return []
        elif DATA_SOURCE_TYPE == "api":
            try:
                logger.info(f"Fetching data from API: {API_URL}")
                r = requests.get(API_URL, timeout=30)
                r.raise_for_status()
                data = r.json()
                if not isinstance(data, list):
                    logger.error(f"API must return a JSON array, got: {type(data)}")
                    return []
                logger.info(f"Fetched {len(data)} records from API")
                return data
            except Exception as e:
                logger.error(f"API fetch failed: {e}")
                return []
        logger.error(f"Unknown DATA_SOURCE_TYPE: {DATA_SOURCE_TYPE}")
        return []

    def _compute_data_hash(self, records: List[Dict]) -> str:
        """Compute hash of records to detect changes."""
        data_str = json.dumps(records, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _get_saved_hash(self) -> Optional[str]:
        """Get previously saved data hash."""
        if os.path.exists(DATA_HASH_PATH):
            try:
                with open(DATA_HASH_PATH, "r") as f:
                    return f.read().strip()
            except Exception:
                return None
        return None

    def _save_hash(self, data_hash: str):
        """Save data hash to file."""
        try:
            with open(DATA_HASH_PATH, "w") as f:
                f.write(data_hash)
        except Exception as e:
            logger.error(f"Failed to save data hash: {e}")

    def build_index(self, records: List[Dict], force: bool = False) -> int:
        """
        Build FAISS index from records and save to disk.

        Args:
            records: List of records to index
            force: If True, rebuild even if data hasn't changed

        Returns:
            Number of records indexed
        """
        if not records:
            logger.warning("No records to index.")
            return 0

        # Check if data has changed using hash
        if not force:
            current_hash = self._compute_data_hash(records)
            saved_hash = self._get_saved_hash()
            if saved_hash == current_hash:
                logger.info("Data unchanged (hash match), skipping rebuild.")
                return len(records)

        with self._lock:
            logger.info(f"Building index for {len(records)} records...")
            start_time = time.time()

            # Convert records to text (simple concatenation). Adjust as needed.
            texts = [self._record_to_text(r) for r in records]

            # Encode with optimized batch size and workers
            logger.info(f"Encoding {len(texts)} texts (batch_size={BATCH_SIZE})...")
            embeddings = self.model.encode(texts)
            d = embeddings.shape[1]

            # Create FAISS index (consider using IndexIVFFlat for large datasets)
            logger.info("Creating FAISS index...")
            index = faiss.IndexFlatL2(d)
            index.add(embeddings)

            # Save to disk
            try:
                logger.info("Saving index to disk...")
                faiss.write_index(index, EMBEDDING_INDEX_PATH)
                with open(METADATA_STORE_PATH, "w", encoding="utf-8") as f:
                    json.dump(records, f, indent=2)

                # Save data hash
                current_hash = self._compute_data_hash(records)
                self._save_hash(current_hash)

                logger.info(f"✓ Index saved to {EMBEDDING_INDEX_PATH}")
            except Exception as e:
                logger.error(f"Failed to save index: {e}")
                raise

            self.index = index
            self.metadata = records

            elapsed = time.time() - start_time
            logger.info(f"✓ Built index for {len(records)} records in {elapsed:.2f}s ({len(records)/elapsed:.1f} records/sec)")
            return len(records)

    def add_records(self, new_records: List[Dict]) -> int:
        """Append new records to index (simple rebuild pattern for reliability)."""
        logger.info(f"Adding {len(new_records)} new records...")
        all_records = self.metadata + new_records
        return self.build_index(all_records)

    def refresh_from_source(self) -> int:
        """Load data from source and rebuild index if changed."""
        records = self._load_records()
        if not records:
            logger.warning("No records loaded from source for refresh.")
            return 0
        # build_index now handles hash comparison internally
        return self.build_index(records, force=False)

    def _record_to_text(self, r: Dict) -> str:
        # Concatenate important fields into a summary string used for embedding
        parts = []
        for k in ["software", "server", "location", "license"]:
            if k in r and r[k] is not None:
                parts.append(str(r[k]))
        # Add numeric fields too for context
        numeric_keys = ["latest_license_issued", "license_day_peak", "license_day_average",
                        "license_work_peak", "license_work_average", "percentage_work_peak", "percentage_work_average"]
        for k in numeric_keys:
            if k in r:
                parts.append(f"{k}:{r[k]}")
        return " | ".join(parts)

    def query(self, q: str, k: int = 6) -> List[Dict]:
        """Query the index for similar records. Lazily builds index if needed."""
        # Lazy load: build index if not initialized and LAZY_LOAD is enabled
        if not self._initialized and LAZY_LOAD:
            logger.info("First query received - building index now (lazy load)...")
            try:
                count = self.refresh_from_source()
                if count > 0:
                    self._initialized = True
                    logger.info(f"✓ Index built with {count} records.")
                else:
                    logger.warning("No data available for indexing.")
                    return []
            except Exception as e:
                logger.error(f"Lazy index build failed: {e}")
                return []

        if self.index is None or len(self.metadata) == 0:
            logger.warning("Index is empty, cannot query.")
            return []

        with self._lock:
            q_emb = self.model.encode([q])
            # Ensure k doesn't exceed number of indexed items
            k = min(k, len(self.metadata))
            D, I = self.index.search(q_emb, k)

            results = []
            for idx in I[0]:
                if 0 <= idx < len(self.metadata):
                    results.append(self.metadata[idx])

        logger.info(f"Query returned {len(results)} results.")
        return results

    def _auto_refresh_loop(self):
        """Background thread that periodically refreshes the index from source."""
        logger.info(f"Auto-refresh loop started (interval: {REFRESH_INTERVAL}s)")

        while True:
            time.sleep(REFRESH_INTERVAL)
            try:
                logger.info("Starting auto-refresh...")
                count = self.refresh_from_source()
                if count:
                    logger.info(f"Auto-refreshed and indexed {count} records.")
            except Exception as e:
                logger.error(f"Auto-refresh error: {e}")
