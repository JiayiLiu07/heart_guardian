import os
import json
import hashlib

CACHE_DIR = "cache"

def cache_response(key, response):
    """Cache a response to a file using a hash key."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"{hashlib.md5(key.encode()).hexdigest()}.json")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump({"response": response}, f, ensure_ascii=False)

def load_cached_response(key):
    """Load a cached response from a file."""
    cache_file = os.path.join(CACHE_DIR, f"{hashlib.md5(key.encode()).hexdigest()}.json")
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f).get("response")
    return None