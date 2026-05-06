# Tutorial 11: Containerise and Ship a Three-Tier Application

A new starter on your team has written a small "bookshop" service — a FastAPI backend, a static web frontend, and a Postgres database — and committed it as one folder of source code. It runs on her laptop. Your job is to turn it into something that runs identically on any machine with Docker installed: pinned dependencies, multi-stage Dockerfiles, a Compose file with health checks and secrets, an SBOM, a vulnerability scan, and a deliberate rollback drill. By the end, you will have the same artefact running locally that you would ship to a small production host — and you will have rolled it back to the previous version once on purpose.

**Concepts covered:** Multi-stage Dockerfiles, image digest pinning, Docker Compose, health checks, named volumes, secrets, semantic versioning, SBOMs (Syft), image scanning (Trivy), Dockerfile linting (hadolint), rolling deploys, rollback

**Format:** Individual or pairs | **Duration:** ~2 hours | **Tool:** Docker · Docker Compose · Python · FastAPI · Postgres · Syft · Trivy · hadolint · Git

---

## Outline

- [Part A: Build the Three-Tier Compose Stack](#part-a-build-the-three-tier-compose-stack-60-min)
- [Part B: Version, Scan, and Practise Rollback](#part-b-version-scan-and-practise-rollback-60-min)
- [References](#references)

---

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Write a multi-stage Dockerfile that produces a small, non-root, health-checked image for a Python service.
2. Compose a `web + api + db` stack with named volumes, secrets, and `depends_on: condition: service_healthy`.
3. Pin every base image and dependency by digest and version, so the same source produces the same artefact tomorrow.
4. Generate a Software Bill of Materials with Syft and scan an image for known CVEs with Trivy.
5. Tag an image with `MAJOR.MINOR.PATCH+sha.<commit>` and roll back to the previous tag when a release is broken.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) ≥ 4.30 (includes Docker Engine and Compose v2)
- [Git](https://git-scm.com/) — installed in Tutorial 1
- A terminal, a code editor (VS Code), and roughly 3 GB of free disk space for images

Verify Docker is working before continuing:

```bash
docker version
docker compose version
```

Both commands should print version numbers without errors.

---

## Part A: Build the Three-Tier Compose Stack *(~60 min)*

You will build a small bookshop service with three containers: a Postgres database, a FastAPI API that reads and writes books, and a static web page that lists them. Each container has a single, focused responsibility — the same shape as a real production system, just smaller.

### Step 1: Scaffold the Project

```bash
mkdir bookshop && cd bookshop
git init
mkdir -p api web secrets
```

Add a `.gitignore` so you do not accidentally commit secrets or local volumes:

```bash
cat > .gitignore <<'EOF'
secrets/*
!secrets/.gitkeep
.env
__pycache__/
*.pyc
.venv/
EOF

touch secrets/.gitkeep
```

The `secrets/` directory is empty in version control; only the placeholder `.gitkeep` is tracked. The actual secret files are written locally in the next step and never committed.

---

### Step 2: Create the Database Password Secret

```bash
# Generate a random 32-character password and store it as a file.
openssl rand -base64 24 > secrets/db_password.txt
chmod 600 secrets/db_password.txt
```

The password lives in a file with restricted permissions. Compose will mount it inside containers at `/run/secrets/db_password` — never as an environment variable, never in the image.

> **Why a file and not an environment variable?** Environment variables show up in `docker inspect`, in `ps`, in crash dumps, and in any framework that logs its config on startup. Files mounted as Compose secrets do not.

---

### Step 3: Write the FastAPI Service

Create `api/main.py`:

```python
# api/main.py
"""Minimal bookshop API: list and add books."""
import os
from contextlib import asynccontextmanager
from pathlib import Path

import asyncpg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "bookshop")
DB_NAME = os.getenv("DB_NAME", "bookshop")
DB_PASSWORD_FILE = os.getenv("DB_PASSWORD_FILE", "/run/secrets/db_password")
APP_VERSION = os.getenv("APP_VERSION", "0.0.0+local")


def read_password() -> str:
    return Path(DB_PASSWORD_FILE).read_text().strip()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=read_password(), database=DB_NAME,
        min_size=1, max_size=5,
    )
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id    SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL
            )
            """
        )
    yield
    await app.state.pool.close()


app = FastAPI(lifespan=lifespan)


class Book(BaseModel):
    title: str
    author: str


@app.get("/healthz")
async def healthz():
    try:
        async with app.state.pool.acquire() as conn:
            await conn.execute("SELECT 1")
        return {"status": "ok", "version": APP_VERSION}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"db unreachable: {exc}")


@app.get("/books")
async def list_books():
    async with app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, title, author FROM books ORDER BY id")
    return [dict(r) for r in rows]


@app.post("/books", status_code=201)
async def add_book(book: Book):
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO books (title, author) VALUES ($1, $2) RETURNING id",
            book.title, book.author,
        )
    return {"id": row["id"], **book.model_dump()}
```

Create `api/requirements.txt` with pinned versions:

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
asyncpg==0.29.0
pydantic==2.9.2
```

> **Why pin every version?** A free-floating `fastapi` resolves to today's latest version on every build. In six months "the same Dockerfile" produces a different image, with different transitive dependencies, and possibly a different bug. Pinning is the contract that makes the build reproducible.

---

### Step 4: Write the Multi-stage Dockerfile for the API

Create `api/Dockerfile`:

```dockerfile
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
```

> **The digest in `FROM python:3.12.6-slim-bookworm@sha256:...` is illustrative.** Run `docker pull python:3.12.6-slim-bookworm` and `docker inspect --format='{{index .RepoDigests 0}}' python:3.12.6-slim-bookworm` to get the real digest for your machine, and substitute it. The exact value will differ between architectures (amd64 vs. arm64) and over time as the upstream tag is rebuilt.

Several things in this file are doing real work, and the chapter (§11.7 and §11.12) walks through why each matters:

- **Two stages** — the build stage carries `gcc` and `libpq-dev` for compiling `asyncpg`'s C extension; the runtime stage carries neither. The final image is roughly 90 MB smaller.
- **`USER app`** — the container does not run as root. A vulnerability in FastAPI does not become a kernel-adjacent compromise.
- **`HEALTHCHECK`** — Compose uses this to decide when the API is ready, not just running. Without it, the web service starts before the API is listening, and the first page load fails.
- **`--start-period=20s`** — gives the API time to connect to Postgres and run `CREATE TABLE` before failing checks count.

---

### Step 5: Write the Static Web Frontend

The web tier is deliberately minimal — a single HTML page served by nginx that calls the API. Keeping it small lets the tutorial focus on the Compose plumbing.

Create `web/index.html`:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Bookshop</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 40rem; margin: 2rem auto; }
    form { display: flex; gap: 0.5rem; margin: 1rem 0; }
    input { flex: 1; padding: 0.5rem; }
    li { padding: 0.25rem 0; }
    .meta { color: #888; font-size: 0.85rem; }
  </style>
</head>
<body>
  <h1>Bookshop</h1>
  <p class="meta" id="meta">Loading…</p>
  <ul id="books"></ul>
  <form id="add">
    <input name="title" placeholder="Title" required />
    <input name="author" placeholder="Author" required />
    <button type="submit">Add</button>
  </form>
  <script>
    async function load() {
      const meta = document.getElementById("meta");
      const list = document.getElementById("books");
      try {
        const [books, health] = await Promise.all([
          fetch("/api/books").then(r => r.json()),
          fetch("/api/healthz").then(r => r.json()),
        ]);
        meta.textContent = `API ${health.version} — ${books.length} book(s)`;
        list.innerHTML = books
          .map(b => `<li><strong>${b.title}</strong> — ${b.author}</li>`)
          .join("");
      } catch (e) {
        meta.textContent = "API unreachable: " + e;
      }
    }
    document.getElementById("add").addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const f = ev.target;
      await fetch("/api/books", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ title: f.title.value, author: f.author.value }),
      });
      f.reset();
      load();
    });
    load();
  </script>
</body>
</html>
```

Create `web/nginx.conf` so nginx reverse-proxies `/api/*` to the API service:

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    location /api/ {
        proxy_pass http://api:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Create `web/Dockerfile`:

```dockerfile
# web/Dockerfile
FROM nginx:1.27.1-alpine@sha256:6a2f8b28e45c4adea04ec207a251fd4a2df03ddc930f782af51e315ebc76e9a9

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html

# nginx images already define HEALTHCHECK-friendly behaviour via default port 80,
# but adding an explicit one documents intent.
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
    CMD wget -q -O- http://localhost/ >/dev/null || exit 1
```

Replace the digest with the value `docker inspect` reports for your platform, as for the API.

---

### Step 6: Write the Compose File

Create `compose.yaml` at the project root:

```yaml
name: bookshop

services:
  db:
    image: postgres:16.4-alpine@sha256:1fe1a99ed9fa2c46f37c5f5d22e75c84cf76f17e5eb1cf2d066eedca50f7c3f4
    environment:
      POSTGRES_USER: bookshop
      POSTGRES_DB: bookshop
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - db-data:/var/lib/postgresql/data
    secrets:
      - db_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U bookshop -d bookshop"]
      interval: 5s
      timeout: 3s
      retries: 5
    restart: unless-stopped

  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    image: bookshop-api:${APP_VERSION:-dev}
    environment:
      DB_HOST: db
      DB_USER: bookshop
      DB_NAME: bookshop
      DB_PASSWORD_FILE: /run/secrets/db_password
      APP_VERSION: ${APP_VERSION:-dev}
    secrets:
      - db_password
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  web:
    build:
      context: ./web
      dockerfile: Dockerfile
    image: bookshop-web:${APP_VERSION:-dev}
    ports:
      - "8080:80"
    depends_on:
      api:
        condition: service_healthy
    restart: unless-stopped

volumes:
  db-data:

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

A few decisions worth naming:

- The database publishes **no host port**. The API talks to it over the private Compose network at `db:5432`. A common AI-generated mistake is to publish `5432:5432` "for debugging" and forget to remove it.
- `depends_on: condition: service_healthy` for the API and web services. Without this, the API starts before Postgres is accepting connections and crash-loops; the web tier starts before the API is ready and serves an error on first load.
- `image: bookshop-api:${APP_VERSION:-dev}` — Compose builds the image *and* tags it with whatever `APP_VERSION` you set in the environment. This is what makes Part B's rollback drill possible.

---

### Step 7: Bring Up the Stack

```bash
docker compose up --build -d
docker compose ps
```

Expected: three services, all `healthy` after about 20 seconds. If any are `unhealthy`, inspect logs:

```bash
docker compose logs api
```

Open `http://localhost:8080` in a browser. The page should report `API dev — 0 book(s)`. Add a book through the form; the list updates.

Verify the health endpoints from the host:

```bash
curl -s http://localhost:8080/api/healthz
```

Expected: `{"status":"ok","version":"dev"}`.

Commit the working stack:

```bash
git add .
git commit -m "feat: bookshop three-tier stack with compose"
```

Tear down between sessions but keep the database volume:

```bash
docker compose down       # stops containers; volume persists
# docker compose down -v  # would also delete the named volume — be careful
```

---

## Part B: Version, Scan, and Practise Rollback *(~60 min)*

A working stack is not a shippable stack. Part B adds the four release-engineering disciplines from Chapter 11: pin everything, generate an SBOM, scan for vulnerabilities, and prove you can roll back.

### Step 1: Tag an Image with SemVer + Commit SHA

Set an `APP_VERSION` derived from a Git tag and the short commit SHA:

```bash
git tag v1.0.0
export APP_VERSION="1.0.0+sha.$(git rev-parse --short HEAD)"
echo "Building $APP_VERSION"

docker compose build
```

Inspect the resulting tags:

```bash
docker images bookshop-api bookshop-web
```

You should see entries like `bookshop-api:1.0.0+sha.abc1234` and `bookshop-web:1.0.0+sha.abc1234`. Restart the stack so the running containers are the tagged ones:

```bash
docker compose up -d
curl -s http://localhost:8080/api/healthz
```

The `version` field in the response now reads `1.0.0+sha.abc1234`. Whatever else changes, the version a user sees in the UI is now traceable back to a specific commit.

> **Why include the commit SHA in the version?** SemVer alone tells you the contract (1.0.0 means a stable, public API). The `+sha.abc1234` build metadata tells you *exactly which commit* produced the running binary. During incident response that distinction is the difference between "we shipped the patch" and "we shipped the patch *and* this is the one running on the host that is on fire."

---

### Step 2: Generate a Software Bill of Materials with Syft

Install Syft (if not already on your machine):

```bash
# macOS / Linux
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh \
  | sh -s -- -b /usr/local/bin

syft version
```

Generate the SBOM for the API image in CycloneDX format:

```bash
syft "bookshop-api:${APP_VERSION}" -o cyclonedx-json > sbom-api.json
```

Inspect what is inside:

```bash
syft "bookshop-api:${APP_VERSION}" -o table | head -30
```

You should see every Python package (FastAPI, uvicorn, pydantic, asyncpg) and every Debian package (libpq5, curl, libssl) with its exact version. **Commit the SBOM** so you can answer supply-chain questions about this specific build months from now:

```bash
git add sbom-api.json
git commit -m "chore: add SBOM for bookshop-api 1.0.0"
```

---

### Step 3: Scan the Image with Trivy

Install Trivy:

```bash
# macOS
brew install trivy
# Linux
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh \
  | sh -s -- -b /usr/local/bin
```

Scan the API image for known CVEs:

```bash
trivy image --severity HIGH,CRITICAL "bookshop-api:${APP_VERSION}"
```

If you see HIGH or CRITICAL findings, three responses are reasonable:

1. **Bump the base image** — most findings will be in the Debian or Alpine base. Pull the latest patch of `python:3.12.6-slim-bookworm` (or move to the next patch release) and rebuild.
2. **Bump a Python dependency** — if the finding is in FastAPI or asyncpg, update `requirements.txt` to a fixed version.
3. **Document an accepted risk** — if no fix is available and the vulnerability is not exploitable in your context, file it under `.trivyignore` with a justification *and a date to revisit*.

Run the scan in a way that fails CI on any HIGH or CRITICAL finding:

```bash
trivy image --severity HIGH,CRITICAL --exit-code 1 \
    "bookshop-api:${APP_VERSION}"
echo "exit: $?"
```

Exit code 0 means clean. Exit code 1 means at least one finding — useful as a CI gate.

---

### Step 4: Lint the Dockerfiles with hadolint

```bash
docker run --rm -i hadolint/hadolint < api/Dockerfile
docker run --rm -i hadolint/hadolint < web/Dockerfile
```

`hadolint` reports things like:

- `DL3008` — pinning `apt` package versions
- `DL3009` — cleaning the apt cache after install
- `DL3007` — using `:latest` as a base tag

Fix every finding you can. Real production projects either fix all findings or commit a `.hadolint.yaml` listing accepted exceptions, with a reason for each.

---

### Step 5: Practise a Rollback Drill

Now make a deliberately broken release and roll back. Edit `api/main.py` to break the health check:

```python
# api/main.py — change /healthz
@app.get("/healthz")
async def healthz():
    raise HTTPException(status_code=500, detail="deliberately broken for rollback drill")
```

Build and tag as `v1.1.0`:

```bash
git add api/main.py
git commit -m "feat: ship broken v1.1.0 (rollback drill)"
git tag v1.1.0
export APP_VERSION="1.1.0+sha.$(git rev-parse --short HEAD)"

docker compose build
docker compose up -d
```

Wait 30 seconds and check status:

```bash
docker compose ps
```

The `api` service will be `unhealthy`. Crucially, the **web service is still running** because it started before the new API rolled out — but every request to `/api/*` now returns 500.

Roll back. The previous image is still on disk under its earlier tag; switch the running container back to it:

```bash
# Identify the previous version tag.
docker images bookshop-api --format "{{.Tag}}"
# Pick the previous (1.0.0+sha.<old>) and restart with it.
export APP_VERSION="1.0.0+sha.<old-sha>"

# Re-pin the *image* without rebuilding, by passing it explicitly:
docker compose up -d --no-build
```

Within seconds the API is healthy again and the page works. Verify:

```bash
curl -s http://localhost:8080/api/healthz
```

Now ask the more important question: **how long did the rollback take?** If it took longer than five minutes, the rollback procedure itself is a defect — fix it before shipping anything that matters. Possible improvements:

- Keep the previous-version tag in an `APP_VERSION_PREVIOUS` environment variable, recorded automatically at every deploy, so the rollback is one command.
- Script the rollback as `./scripts/rollback.sh` so the procedure is the same every time, including at 2 a.m.

Reset the broken commit (or revert it on a branch) before continuing:

```bash
git revert HEAD --no-edit
docker compose build
export APP_VERSION="1.2.0+sha.$(git rev-parse --short HEAD)"
docker compose up -d
```

---

### Step 6: Activity — Audit an AI-generated Compose File

Ask a coding agent (Claude Code, Copilot, or similar) the following exact prompt:

> Generate a `docker-compose.yml` for a Postgres database, a Node.js API, and an Nginx web server. Make it production-ready.

Save the response as `agent-compose.yaml` (do not run it). Audit it against the eight-item checklist below. For each defect, write a one-line note on the *production failure mode* — not just the rule violated. Section 11.12 of Chapter 11 lists the shapes of failure to watch for.

```markdown
# AI-Generated Compose Audit

| # | Check | Pass / Fail | Production failure mode if failed |
|---|---|---|---|
| 1 | Every image pinned to a specific tag (no `:latest`) |   |   |
| 2 | Every image pinned to a digest (`@sha256:...`) |   |   |
| 3 | Database has a `healthcheck` |   |   |
| 4 | API uses `depends_on: condition: service_healthy` for the database |   |   |
| 5 | Database port is *not* published to the host |   |   |
| 6 | Database password supplied via `secrets:`, not environment variable |   |   |
| 7 | Database state in a *named volume*, not a bind mount or anonymous volume |   |   |
| 8 | API and web services have an explicit `restart:` policy |   |   |
```

Commit your audit:

```bash
git add agent-compose.yaml AUDIT.md
git commit -m "docs: audit AI-generated compose file against release-engineering checklist"
```

The point of this activity is not that agents are bad. It is that agents reliably miss exactly the checks that catch incidents. Reviewing for these eight items takes about ninety seconds; the exposure if you skip them is unbounded.

---

## References

- [Docker Compose Specification](https://docs.docker.com/compose/compose-file/) — the authoritative reference for `compose.yaml` keys and behaviour
- [Dockerfile Best Practices](https://docs.docker.com/build/building/best-practices/) — multi-stage, layer caching, image hygiene
- [hadolint](https://github.com/hadolint/hadolint) — Dockerfile linter
- [Syft](https://github.com/anchore/syft) — generate SBOMs from images
- [Trivy](https://aquasecurity.github.io/trivy/) — vulnerability scanner for images, filesystems, and IaC
- [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html) — semantic versioning specification
- [The Twelve-Factor App](https://12factor.net/) — strict separation of build, release, run; config in the environment
- [PostgreSQL Docker image documentation](https://hub.docker.com/_/postgres) — environment variables, volume locations, init scripts
