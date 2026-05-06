import os
from pathlib import Path

UPLOAD_DIR = Path("/app/uploads")

# VULNERABLE: Direct path construction
def read_upload_bad(filename: str) -> bytes:
    path = UPLOAD_DIR / filename  # filename = "../../etc/passwd" would escape!
    with open(path, "rb") as f:
        return f.read()


# SAFE: Resolve and verify the path stays within the intended directory
def read_upload(filename: str) -> bytes:
    requested_path = (UPLOAD_DIR / filename).resolve()

    # is_relative_to checks path hierarchy, not string prefix, avoiding the
    # prefix-collision bug where /app/uploads_secret passes a startswith check
    if not requested_path.is_relative_to(UPLOAD_DIR.resolve()):
        raise PermissionError(f"Access denied: {filename}")

    with open(requested_path, "rb") as f:
        return f.read()
