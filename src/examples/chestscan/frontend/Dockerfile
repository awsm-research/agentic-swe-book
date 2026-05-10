# frontend/Dockerfile
# Single-stage Dockerfile for the ChestScan Streamlit frontend.
#
# Pure-Python dependencies (streamlit, requests, Pillow) require no
# compilation, so a multi-stage build is not needed here.
#
# Security:
#   - Non-root user (appuser, UID 1001)
#   - No build tools in the runtime image
#   - Health check on Streamlit's built-in health endpoint

FROM python:3.11-slim

LABEL org.opencontainers.image.title="ChestScan Frontend"
LABEL org.opencontainers.image.description="Streamlit radiologist interface for chest X-ray classification"

# curl for HEALTHCHECK
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home --shell /bin/false appuser

WORKDIR /app

# Install Python dependencies (as root, before switching user)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit application
COPY --chown=appuser:appgroup app.py .

# Switch to non-root user
USER appuser

# Expose Streamlit's default port
EXPOSE 8501

# Health check against Streamlit's built-in health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/healthz || exit 1

# Run Streamlit in headless server mode
CMD ["streamlit", "run", "app.py", \
     "--server.address", "0.0.0.0", \
     "--server.port", "8501", \
     "--server.headless", "true"]
