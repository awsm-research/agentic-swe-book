# test_path.py
from flask import request
import os

def download_file():
    filename = request.args.get("file")
    path = os.path.join("/uploads", filename)   # ← should trigger
    with open(path) as f:
        return f.read()

def safe_download():
    filename = request.args.get("file")
    base = "/uploads"
    path = os.path.realpath(os.path.join(base, filename))
    if not path.startswith(base):
        raise ValueError("Path traversal attempt")
    with open(path) as f:
        return f.read()
