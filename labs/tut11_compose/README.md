# Tutorial 11 — Bookshop Three-Tier Compose Stack

The complete bookshop application from Tutorial 11 Part A — FastAPI API,
nginx static frontend, and Postgres database, wired together with Compose
secrets, health checks, and `depends_on: condition: service_healthy`.

## Files

```
tut11_compose/
├── compose.yaml              # three services + volume + secret
├── .gitignore                # excludes real secrets and the venv
├── api/
│   ├── Dockerfile            # multi-stage, non-root, healthchecked
│   ├── main.py               # FastAPI bookshop API
│   └── requirements.txt      # pinned dependencies
├── web/
│   ├── Dockerfile            # nginx with bundled config + index.html
│   ├── index.html            # static frontend that calls /api/*
│   └── nginx.conf            # reverse proxies /api/ to api:8000
└── secrets/
    └── .gitkeep              # placeholder; the real db_password.txt is gitignored
```

## Important: substitute real digests

Both Dockerfiles and `compose.yaml` pin base images by digest. The values
shipped here are the illustrative digests from the tutorial — they may not be
valid for your platform. Run:

```bash
docker pull python:3.12.6-slim-bookworm
docker inspect --format='{{index .RepoDigests 0}}' python:3.12.6-slim-bookworm

docker pull nginx:1.27.1-alpine
docker inspect --format='{{index .RepoDigests 0}}' nginx:1.27.1-alpine

docker pull postgres:16.4-alpine
docker inspect --format='{{index .RepoDigests 0}}' postgres:16.4-alpine
```

Substitute the real digests before building.

## How to run

```bash
# Generate the database password secret first.
openssl rand -base64 24 > secrets/db_password.txt
chmod 600 secrets/db_password.txt

# Build and start the stack.
docker compose up --build -d
docker compose ps

# Hit the web frontend.
open http://localhost:8080
curl -s http://localhost:8080/api/healthz
```

## Tag and roll back (Part B)

```bash
git tag v1.0.0
export APP_VERSION="1.0.0+sha.$(git rev-parse --short HEAD)"
docker compose build
docker compose up -d

# Generate SBOM and scan.
syft "bookshop-api:${APP_VERSION}" -o cyclonedx-json > sbom-api.json
trivy image --severity HIGH,CRITICAL "bookshop-api:${APP_VERSION}"
```
