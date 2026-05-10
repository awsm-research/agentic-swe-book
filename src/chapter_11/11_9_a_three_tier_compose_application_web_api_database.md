## 11.9 A Three-Tier Compose Application: Web + API + Database

The worked example for the rest of the chapter is the simplest non-trivial system: a web frontend that talks to an API server that talks to a Postgres database.

```
+----------+       +----------+       +-----------+
|   web    | ----> |   api    | ----> |    db     |
| Next.js  |  HTTP | FastAPI  |  TCP  | Postgres  |
| :3000    |       | :8000    |       | :5432     |
+----------+       +----------+       +-----------+
                                            |
                                            v
                                      named volume
                                      (db-data)
```

The Compose file:

```yaml
name: bookshop

services:
  db:
    image: postgres:16.4-alpine@sha256:1f1f...
    environment:
      POSTGRES_USER: bookshop
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
      POSTGRES_DB: bookshop
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
    environment:
      DATABASE_URL: postgresql://bookshop@db:5432/bookshop
      DATABASE_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-q", "-O-", "http://localhost:8000/healthz"]
      interval: 10s
      timeout: 3s
      retries: 3
    restart: unless-stopped

  web:
    build:
      context: ./web
      dockerfile: Dockerfile
    environment:
      API_URL: http://api:8000
    ports:
      - "3000:3000"
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

Several decisions in this file are worth examining, because every one of them is something an AI agent will commonly get wrong if not asked specifically.

### Service Networking

Compose creates a default network for the project. Services address each other by service name — the API connects to Postgres at `db:5432`, not `localhost:5432` and not the host's IP. Only the `web` service publishes a port to the host (`3000:3000`); `api` and `db` are reachable only inside the network. This is correct production posture: the database is not exposed to the public internet, and the API is reached through the web frontend. A common AI-generated mistake is to publish `5432:5432` for the database "for debugging" and forget to remove it.

### Named Volumes vs. Bind Mounts

The Postgres data lives in a *named volume* (`db-data`), not a bind mount to the host filesystem. Named volumes are managed by Docker, persist across container rebuilds, and survive `docker compose down` (use `docker compose down -v` to actually remove them — and write that down, because the muscle memory will eventually delete a production database). Bind mounts (`./pgdata:/var/lib/postgresql/data`) are appropriate for *configuration* (mounting a config file into a container) but not for *state* (Postgres data, uploaded files), because file ownership and permissions on bind mounts are the host's, not the container's, and that mismatch causes silent corruption.

### Health Checks and `depends_on`

`depends_on: db` only guarantees that the DB *container* started before the API; it says nothing about whether Postgres is *ready to accept connections*. The API will start, fail to connect, and crash-loop. The fix is `condition: service_healthy`, which makes Compose wait for the DB's `HEALTHCHECK` to report healthy before starting the API. Health checks are not optional in a Compose file with multiple services. This is the single most common AI omission in generated Compose files.

### Secrets

The Postgres password is supplied as a Compose *secret*, not an environment variable. Environment variables show up in `ps`, `docker inspect`, log lines, and crash dumps. Compose secrets are mounted as files inside the container at `/run/secrets/<name>`, with restricted permissions, and never serialised into image metadata. The slightly clunky `_FILE` suffix convention (`POSTGRES_PASSWORD_FILE`, `DATABASE_PASSWORD_FILE`) is supported by most well-written images.

### Configuration via `.env`

Twelve-factor configuration says: *configuration that varies between deploys lives in the environment, not in the image*. In practice, Compose reads a `.env` file in the project root and substitutes `${VAR}` references. The same Compose file ships to staging and production; only the `.env` file (and the secrets) differ.

```
# .env (committed as .env.example; real .env is gitignored)
POSTGRES_VERSION=16.4
API_PORT=8000
WEB_PORT=3000
LOG_LEVEL=info
```

Two pitfalls, both common in AI-generated stacks. First, the real `.env` is committed to the repository — passwords leak to the world. The `.env` file belongs in `.gitignore`; a `.env.example` with placeholder values is what gets committed. Second, secrets are stuffed into `.env` because it is convenient — combine with the first pitfall and you have a known anti-pattern.

### What Goes Wrong in Practice

Even with this template, a Compose stack will surprise you. The recurring failures:

- **Port collisions** — port 5432 is already in use because Postgres is also installed on the host.
- **Mounting `node_modules` from the host** — bind-mounting the source directory shadows the container's `node_modules`, which was built for Linux. The container then tries to load the host's macOS-built native binaries and crashes.
- **Forgotten migrations** — the API expects schema v17, the database is at v16 because nobody ran `alembic upgrade head` after deploy.
- **Postgres minor-version surprises** — `postgres:16` was 16.3 yesterday and is 16.4 today; a minor upgrade ran on first boot, and a column type changed somewhere in the release notes.

The mitigation for all four is the same: **pin everything by digest, run migrations as a deliberate step, and never reach across the container boundary for native dependencies.**

---
