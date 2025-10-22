# 📁 utils/cache.py
import streamlit as st
import json
import os
import hashlib

# Define a cache directory, e.g., './.streamlit_cache/'
CACHE_DIR = "./.streamlit_cache/"

# Ensure the cache directory exists
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def generate_cache_key(key_prefix: str, *args, **kwargs) -> str:
    """Generates a cache key based on a prefix and function arguments."""
    # Combine arguments into a stable string representation
    args_str = "".join(str(arg) for arg in args)
    kwargs_str = "".join(f"{k}{v}" for k, v in sorted(kwargs.items()))
    raw_key = f"{key_prefix}_{args_str}_{kwargs_str}"
    
    # Use SHA256 for a stable and robust hash
    return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

def load_cached_response(cache_key: str):
    """Loads a response from the cache file."""
    cache_file_path = os.path.join(CACHE_DIR, f"{cache_key}.json")
    if os.path.exists(cache_file_path):
        try:
            with open(cache_file_path, 'r', encoding='utf-8') as f:
                # Load from JSON. Assumes cached data is JSON serializable.
                # For complex objects, you might need pickle.
                return json.load(f)
        except Exception as e:
            # Log error but don't crash if cache is corrupted
            print(f"Error loading cache file {cache_file_path}: {e}")
            return None
    return None

def save_cached_response(cache_key: str, response):
    """Saves a response to a cache file."""
    cache_file_path = os.path.join(CACHE_DIR, f"{cache_key}.json")
    try:
        with open(cache_file_path, 'w', encoding='utf-8') as f:
            # Save to JSON. Assumes response is JSON serializable.
            json.dump(response, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        # Log error but don't crash
        print(f"Error saving to cache file {cache_file_path}: {e}")
        return False

# Example of using Streamlit's cache_data decorator with custom logic (optional)
# @st.cache_data(experimental_allow_widgets=True) # Allow widgets if needed
# def cached_function_with_custom_key(arg1, arg2, custom_key_prefix="my_func"):
#     cache_key = generate_cache_key(custom_key_prefix, arg1, arg2)
#     cached_data = load_cached_response(cache_key)
#     if cached_data is not None:
#         return cached_data
#     
#     # Simulate computation
#     result = f"Computed result for {arg1} and {arg2}"
#     save_cached_response(cache_key, result)
#     return result