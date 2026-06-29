import os
import json
import hashlib
import math
from typing import Optional, Any, List, Tuple
from app.core.cache.base import BaseCache

# Attempt lazy load of sentence-transformers
_MODEL = None
def _get_embedding_model():
    global _MODEL
    if _MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Use small/efficient embedding model
            _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _MODEL = "FALLBACK"
    return _MODEL

def get_embedding(text: str) -> List[float]:
    """Generates an embedding vector. Falls back to TF-IDF word frequency representation if SentenceTransformer is offline."""
    model = _get_embedding_model()
    if model != "FALLBACK" and model is not None:
        try:
            vector = model.encode(text).tolist()
            return vector
        except Exception:
            pass
            
    # TF-IDF fallback vector: list of frequencies of words in a fixed-size vocabulary
    words = [w.lower() for w in text.split() if len(w) > 2]
    # Simple hash-trick to project text to 128-dimensional frequency space
    vector = [0.0] * 128
    for w in words:
        h = int(hashlib.md5(w.encode("utf-8")).hexdigest(), 16) % 128
        vector[h] += 1.0
        
    # Normalize vector to unit length
    magnitude = math.sqrt(sum(x * x for x in vector))
    if magnitude > 0:
        vector = [x / magnitude for x in vector]
    return vector

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if len(v1) != len(v2) or not v1:
        return 0.0
    dot_product = sum(x * y for x, y in zip(v1, v2))
    norm_a = math.sqrt(sum(x * x for x in v1))
    norm_b = math.sqrt(sum(x * x for x in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)

class SemanticCache(BaseCache):
    """Redis-based semantic cache utilizing cosine similarity vector lookups and workspace isolation."""
    
    def __init__(self):
        super().__init__(ttl=int(os.getenv("CACHE_TTL_SEMANTIC", "86400")))  # Default 24 hours
        self._client: Optional[Any] = None
        self._initialized = False
        
    def _get_redis_client(self) -> Optional[Any]:
        if self._initialized:
            return self._client
        self._initialized = True
        try:
            import redis
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self._client = redis.from_url(redis_url, socket_timeout=2, decode_responses=True)
        except Exception:
            self._client = None
        return self._client
        
    def _hash_prompt(self, prompt: str) -> str:
        return hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()
        
    def lookup(self, workspace_id: str, prompt: str, threshold: float = 0.85) -> Optional[Tuple[List[str], str]]:
        """Performs exact hash match first, then falls back to semantic embedding similarity lookup."""
        client = self._get_redis_client()
        prompt_hash = self._hash_prompt(prompt)
        cache_key = f"semantic_cache:{workspace_id}:{prompt_hash}"
        
        # 1. Try exact lookup
        exact_match = self.get(cache_key)
        if exact_match:
            return exact_match.get("response"), "exact"
            
        # If Redis is not available, we fall back to local storage in base class
        if not client:
            return None
            
        # 2. Try semantic similarity search
        try:
            set_key = f"semantic_cache_keys:{workspace_id}"
            all_hashes = client.smembers(set_key)
            if not all_hashes:
                return None
                
            # Fetch all cached entries for workspace
            keys = [f"semantic_cache:{workspace_id}:{h}" for h in all_hashes]
            raw_entries = client.mget(keys)
            
            entries = []
            for r in raw_entries:
                if r:
                    try:
                        entries.append(json.loads(r))
                    except Exception:
                        pass
                        
            if not entries:
                return None
                
            # Generate query embedding
            query_vector = get_embedding(prompt)
            
            best_match = None
            best_score = -1.0
            
            for entry in entries:
                cached_vector = entry.get("embedding")
                if cached_vector:
                    score = cosine_similarity(query_vector, cached_vector)
                    if score > best_score:
                        best_score = score
                        best_match = entry
                        
            if best_score >= threshold and best_match:
                return best_match.get("response"), f"semantic (score: {best_score:.2f})"
                
        except Exception:
            pass
            
        return None
        
    def save(self, workspace_id: str, prompt: str, response: List[str]) -> None:
        """Saves response and embedding vector to Redis with workspace prefix tagging."""
        client = self._get_redis_client()
        prompt_hash = self._hash_prompt(prompt)
        cache_key = f"semantic_cache:{workspace_id}:{prompt_hash}"
        
        # Calculate embedding
        vector = get_embedding(prompt)
        
        entry = {
            "prompt": prompt,
            "embedding": vector,
            "response": response
        }
        
        # Save key
        self.set(cache_key, entry, ttl=self.ttl)
        
        if client:
            try:
                # Add to workspace keys set
                set_key = f"semantic_cache_keys:{workspace_id}"
                client.sadd(set_key, prompt_hash)
                client.expire(set_key, self.ttl)
            except Exception:
                pass
                
    def invalidate_workspace(self, workspace_id: str) -> None:
        """Removes all cached semantic entries associated with the workspace."""
        client = self._get_redis_client()
        
        # Always clean up local storage fallback dict
        prefix = f"semantic_cache:{workspace_id}:"
        keys_to_del_local = [k for k in self._local_storage.keys() if k.startswith(prefix)]
        for k in keys_to_del_local:
            self._local_storage.pop(k, None)
            
        if not client:
            return
            
        try:
            set_key = f"semantic_cache_keys:{workspace_id}"
            all_hashes = client.smembers(set_key)
            if all_hashes:
                keys_to_del = [f"semantic_cache:{workspace_id}:{h}" for h in all_hashes]
                keys_to_del.append(set_key)
                client.delete(*keys_to_del)
        except Exception:
            pass
