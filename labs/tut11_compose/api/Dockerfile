# api/Dockerfile
# ---- build stage: install deps into a virtualenv ----
FROM python:3.12.6-slim-bookworm@sha256:032c52613401895aa3d418a4c563d2d05f993c965a8ea6eb6c5fb0a1c92a8e3f AS build

WORKDIR /app

# System packages needed only at build time.
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir --upgrade pip==24.2 \
 && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ---- runtime stage: copy only what runs ----
FROM python:3.12.6-slim-bookworm@sha256:032c52613401895aa3d418a4c563d2d05f993c965a8ea6eb6c5fb0a1c92a8e3f

WORKDIR /app

# Runtime-only system libs (no compiler).
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 curl \
    && rm -rf /var/lib/apt/lists/*

# Bring across the prepared virtualenv.
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Application code.
COPY main.py ./

# Run as a non-root user.
RUN groupadd -r app && useradd -r -g app -d /app app \
 && chown -R app:app /app
USER app

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/healthz || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
