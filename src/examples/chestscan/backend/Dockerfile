# backend/Dockerfile
# Multi-stage build for the ChestScan FastAPI serving backend.
#
# Stage 1 (builder): installs Python dependencies including compiled wheels.
# Stage 2 (runtime): lean final image — no build tools, non-root user.
#
# The model is NOT baked into the image.  It is loaded from the MLflow
# Model Registry at container startup via MLFLOW_TRACKING_URI and MODEL_NAME
# environment variables.  This decouples the model version from the image
# version, allowing champion promotion without rebuilding the container.

# ============================================================
# Stage 1: Builder — install all dependencies
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Build dependencies required by some compiled wheels (numpy, Pillow, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to exploit Docker layer caching.
# The pip install layer is only rebuilt when requirements.txt changes.
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --target /install -r requirements.txt

# ============================================================
# Stage 2: Runtime — lean final image
# ============================================================
FROM python:3.11-slim AS runtime

LABEL org.opencontainers.image.title="ChestScan Backend"
LABEL org.opencontainers.image.description="FastAPI serving backend for chest X-ray classification"

# Runtime shared libraries only — no compilers or build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user — never run production services as root
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home --shell /bin/false appuser

# Copy installed packages from builder (avoids re-installing in runtime image)
COPY --from=builder /install /usr/local/lib/python3.11/site-packages

# Copy application source files
WORKDIR /app
COPY --chown=appuser:appgroup main.py .
COPY --chown=appuser:appgroup requirements.txt .

# Copy shared modules (must be identical to those used during training)
# These are expected to be copied from the project root into the backend/ build context.
COPY --chown=appuser:appgroup transforms.py .
COPY --chown=appuser:appgroup dataset.py .

# Switch to non-root user before running the server
USER appuser

# Expose the API port
EXPOSE 8000

# Health check — Docker marks the container unhealthy if this fails.
# start_period allows time for the model download from the registry.
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the FastAPI server with a single worker (model is not thread-safe with multiple).
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
