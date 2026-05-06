import pickle
import json

# VULNERABLE: Deserialising untrusted pickle data
def load_session_bad(data: bytes) -> dict:
    return pickle.loads(data)  # Arbitrary code execution on untrusted data!


# SAFE: Use JSON for data serialisation
def load_session(data: str) -> dict:
    session = json.loads(data)
    # Validate the structure before returning
    if not isinstance(session, dict):
        raise ValueError("Invalid session data")
    return session
