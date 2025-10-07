# utils/crypto.py

from cryptography.fernet import Fernet
import os
import base64

# --- Fernet Key Management ---
# It's crucial to load the Fernet key securely, e.g., from environment variables.
# Ensure FERNET_KEY is set in your .env file.
FERNET_KEY = os.environ.get("FERNET_KEY")

if not FERNET_KEY:
    # Fallback: Generate a key if not found. This key will NOT persist between sessions.
    # For production, ALWAYS use a securely stored, persistent key.
    # print("FERNET_KEY not found in environment. Generating a temporary key.")
    # key = Fernet.generate_key()
    # FERNET_KEY = key.decode()
    # print(f"Generated temporary Fernet Key: {FERNET_KEY}")
    # In a real app, you would raise an error or log a critical warning here.
    pass # Key will be None if not found and not generated.

# Initialize Fernet cipher suite if key is available
cipher_suite = None
if FERNET_KEY:
    try:
        cipher_suite = Fernet(FERNET_KEY.encode()) # Fernet expects bytes
    except Exception as e:
        print(f"Error initializing Fernet cipher suite: {e}")
        # cipher_suite remains None

# --- Encryption and Decryption Functions ---

def generate_key():
    """Generates a new Fernet key."""
    return Fernet.generate_key()

def encrypt_data(data, cipher=None):
    """
    Encrypts data using Fernet.

    Args:
        data (str or bytes): The data to encrypt.
        cipher (Fernet, optional): An initialized Fernet cipher suite. If None, it uses the global one.

    Returns:
        bytes: The encrypted data, or None if encryption fails.
    """
    if cipher is None:
        cipher = cipher_suite
        
    if cipher is None:
        print("Encryption failed: Fernet cipher suite not initialized.")
        return None
        
    try:
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            raise TypeError("Data must be str or bytes")
            
        encrypted_bytes = cipher.encrypt(data_bytes)
        # Optionally, return as base64 string for easier storage in text formats (like JSON, CSV)
        return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
        
    except Exception as e:
        print(f"Encryption error: {e}")
        return None

def decrypt_data(encrypted_data_b64, cipher=None):
    """
    Decrypts Fernet-encrypted data.

    Args:
        encrypted_data_b64 (str or bytes): The base64 encoded encrypted data.
        cipher (Fernet, optional): An initialized Fernet cipher suite. If None, it uses the global one.

    Returns:
        str: The decrypted data, or None if decryption fails.
    """
    if cipher is None:
        cipher = cipher_suite
        
    if cipher is None:
        print("Decryption failed: Fernet cipher suite not initialized.")
        return None
        
    try:
        # Decode from base64 first
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data_b64.encode('utf-8'))
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        return decrypted_bytes.decode('utf-8')
        
    except Exception as e:
        print(f"Decryption error: {e}")
        # This could be due to incorrect key, corrupted data, or wrong format.
        return None

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    if FERNET_KEY:
        print("Fernet key loaded successfully.")
        
        original_data = "This is a secret message."
        print(f"Original data: {original_data}")
        
        encrypted = encrypt_data(original_data)
        if encrypted:
            print(f"Encrypted data (base64): {encrypted}")
            
            decrypted = decrypt_data(encrypted)
            if decrypted:
                print(f"Decrypted data: {decrypted}")
                assert original_data == decrypted
                print("Encryption/Decryption successful!")
            else:
                print("Decryption failed.")
        else:
            print("Encryption failed.")
    else:
        print("Fernet key is not available. Cannot run crypto tests.")
