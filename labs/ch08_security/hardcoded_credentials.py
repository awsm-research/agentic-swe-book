import os

# VULNERABLE: Hardcoded credentials
def connect_bad():
    return DatabaseConnection(
        host="db.example.com",
        password="SuperSecret123!",  # Visible in source code, git history
    )


# SAFE: Read from environment variables
def connect():
    password = os.environ.get("DB_PASSWORD")
    if not password:
        raise EnvironmentError("DB_PASSWORD environment variable is not set")
    return DatabaseConnection(host=os.environ["DB_HOST"], password=password)
