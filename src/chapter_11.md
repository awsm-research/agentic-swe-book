# Chapter 11: From Build to Production — Packaging, Versioning, and Deployment

> *"You ship your org chart. You also ship your build pipeline."*
> — paraphrased from Conway's Law and every release engineer who has ever rolled back a Friday deploy

---

At 04:09 UTC on 19 July 2024, the cybersecurity firm CrowdStrike pushed a routine update to a configuration file used by its Falcon endpoint sensor on Windows. The file — a "channel file" with the extension `.sys` but no executable code — was malformed. Falcon's kernel-mode driver attempted to parse it on boot, dereferenced an invalid pointer, and triggered a bug-check. Approximately 8.5 million Windows hosts entered a continuous boot loop within seventy-eight minutes ([CrowdStrike, 2024](https://www.crowdstrike.com/falcon-content-update-remediation-and-guidance-hub/)). Delta Air Lines alone reported around USD 500 million in losses; hospitals diverted patients; emergency call centres in three US states went dark. The defective file was 42 kilobytes long. The release pipeline pushed it to every customer simultaneously, with no staged rollout, no canary, and no automatic rollback. The defect was tiny. The way it was shipped was the disaster.

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. Apply semantic and calendar versioning conventions and justify the choice for libraries, services, and end-user products.
2. Distinguish the *build*, *package*, and *deploy* stages of a release pipeline and reason about reproducibility and provenance at each boundary.
3. Choose an appropriate packaging format — language artefact, OS package, or OCI container image — for a given delivery context.
4. Containerise a three-tier application (web, API, database) using Docker and Docker Compose, with health checks, volumes, and environment configuration.
5. Compare deployment strategies (recreate, rolling, blue-green, canary, feature flags) and select one for a given risk profile.
6. Evaluate the supply-chain risks of AI-generated Dockerfiles and Compose files, and apply pinning, scanning, and signing controls.

---

## 11.1 Why "It Works on My Machine" Is Not Production

Most production incidents are not caused by code that was wrong. They are caused by code that was correct on the developer's laptop and behaved differently somewhere else. The CrowdStrike outage is an extreme version of this pattern: the channel file passed CrowdStrike's internal validation, was correctly signed, and loaded without complaint on the engineer's test machine. It crashed every Windows kernel that mounted it in production.

The distance between *runs on my machine* and *runs in production* is what release engineering exists to manage. That distance has several axes, and each one is a place where a deploy can go wrong:

- **Environment drift** — the production OS is a different version, has different libraries installed, or runs at higher load than the developer's machine.
- **Dependency drift** — a library version that was pulled at build time is no longer the version present at deploy time.
- **Configuration drift** — secrets, feature flags, and tuning parameters differ between environments and are not version-controlled with the code.
- **Data drift** — production data has shapes the developer never saw: empty strings, multi-byte characters, rows older than the schema migration that was supposed to backfill them.
- **Topology drift** — production runs many instances behind a load balancer, with retries, timeouts, and partial failures that single-process testing never exercises.

A single untested combination of these — an unstaged channel file, a Postgres minor version that auto-upgraded the production volume, a Node base image that silently flipped from `node:20` to `node:22` — is enough to take down a service.

### The Production Gap

Call the union of these axes the *production gap*. The job of a release pipeline is to close the gap, or at least to surface it before customers do. Every practice in this chapter — versioning, lockfiles, immutable artefacts, containers, Compose files, canary deploys — is a tool for shrinking one of those axes. None of them shrinks all five. A team that masters Docker but ignores deployment strategy will still ship CrowdStrike-shaped incidents; a team with a flawless canary process but unpinned base images will still wake up to a Postgres major-version surprise on Monday morning.

The chapter is organised as a walk down those axes, in the order an artefact travels: build, package, deploy, operate.

---

## 11.2 Release Engineering as a Discipline

The term *release engineering* was coined by John O'Duinn and others at Mozilla in the mid-2000s to describe the work of getting Firefox builds reproducibly out the door. Adams and van der Hoek's *Modern Release Engineering* is the canonical academic reference ([Adams & van der Hoek, 2016](https://ieeexplore.ieee.org/document/7383668)); the Google SRE book makes the operational case ([Beyer et al., 2016](https://sre.google/sre-book/release-engineering/)). The two sources converge on four properties a healthy release pipeline buys you.

| Property | What it means | What goes wrong without it |
|---|---|---|
| **Reproducibility** | The same source produces the same artefact, today and in six months | A bug reported against v1.4.2 cannot be reproduced because the build no longer compiles |
| **Traceability** | Every running binary can be mapped back to a commit, a build, and a builder | An incident postmortem cannot determine which change caused the outage |
| **Isolation** | Each environment runs the artefact you intended, not whatever was on disk | A staging fix accidentally activates in production via a shared config file |
| **Reversibility** | A bad release can be rolled back in seconds, not hours | A failing deploy becomes a failing deploy *and* a failing rollback |

These are not aspirational qualities — they are operational necessities. Knight Capital's USD 440 million loss (Chapter 10) was a failure of *isolation*: half the fleet ran the new code, half ran the old. The CrowdStrike incident was a failure of *reversibility*: machines in a boot loop could not download the fix, so recovery required physical access to each host. SolarWinds (2020) was a failure of *traceability*: the malicious build artefact was indistinguishable from a legitimate one because the build environment itself had been compromised.

Release engineering is the discipline that makes these four properties cheap. The rest of the chapter is the practical machinery for doing so.

---

## 11.3 Software Versioning — A Promise to Your Users

A version number is a contract. It tells whoever consumes your software what kind of change they are receiving and how cautious they should be about installing it. If the contract is honest, downstream users can upgrade with confidence; if it is dishonest, they pin to old versions and the ecosystem fragments.

### Semantic Versioning

The dominant convention for libraries is *semantic versioning* (SemVer), formalised by Tom Preston-Werner in 2013 ([SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)). Versions take the form `MAJOR.MINOR.PATCH`, with rules:

- Increment **PATCH** for backwards-compatible bug fixes — the API is unchanged.
- Increment **MINOR** for backwards-compatible additions — new endpoints, new optional parameters.
- Increment **MAJOR** for incompatible changes — removed methods, renamed fields, behavioural changes that break callers.

The contract is that `^1.4.2` (any 1.x version ≥ 1.4.2) is safe to upgrade automatically; a jump to `2.0.0` is not. SemVer works when authors honour it. It fails when they do not — which is most of the time. The Python typing library `typing-extensions` and the JavaScript date library `moment` have both shipped breaking changes in patch releases. Library authors under-version because *their* change feels small; the consumer's broken build is two ecosystems away.

### Calendar Versioning

For products and services, time is often a more honest signal than feature scope. *Calendar versioning* (CalVer) encodes the release date in the version string: `2024.7.1` (year, month, sequence). Ubuntu (`24.04`), JetBrains IDEs (`2024.2`), and pip (`24.1`) all use CalVer. The advantage is that users can see at a glance how old their installation is and whether the security team's "patch within 90 days" policy applies. The disadvantage is that CalVer carries no information about backwards compatibility; consumers must read the changelog rather than trust the number.

A useful rule of thumb: **libraries use SemVer, applications use CalVer.** A library is consumed by other code that needs a compatibility contract; an application is consumed by humans who want to know whether they are running last week's binary.

### Pre-releases and Build Metadata

SemVer also defines suffixes:

- `-alpha`, `-beta`, `-rc.1` — pre-releases, ordered before the unsuffixed version (`1.5.0-rc.1` is older than `1.5.0`).
- `+sha.abc1234` — build metadata, ignored for ordering. Useful for traceability: the version `1.5.0+sha.abc1234` says "release 1.5.0, built from commit abc1234".

Pin pre-release suffixes in lockfiles — `^1.5.0` does not match `1.5.0-rc.1` by default, which has surprised more than one team racing to fix a release-candidate bug.

### Anti-patterns

A few versioning practices are almost always wrong:

- **ZeroVer** — staying on `0.x` forever (`0.142.0`) to "avoid the commitment" of 1.0. The convention is that 0.x has *no* compatibility guarantees, so every minor release can break consumers. If your library has users, ship 1.0.
- **Marketing versions** — jumping from `4.x` to `7.0` because the salesperson wanted a bigger number. This breaks every dependency tool that assumes versions are monotonic.
- **Floating tags in production** — depending on `latest`, `:stable`, or `^1.0.0` in a Dockerfile. The build is no longer reproducible; the same `docker build` next month produces a different image.

### Case: The left-pad and colors.js Incidents

In March 2016, a developer named Azer Koçulu unpublished his eleven-line `left-pad` package from npm after a trademark dispute. Within hours, builds across the JavaScript ecosystem failed — including those of Babel, React, and at one point, Atom — because they depended on `left-pad` transitively, with floating version ranges, and had no local cache ([Williams, 2016](https://www.theregister.com/2016/03/23/npm_left_pad_chaos/)). The ecosystem learned to pin and to mirror.

The lesson did not stick for everyone. In January 2022, the maintainer of the `colors.js` package (used by ~22,000 dependent packages) deliberately published a version that printed `LIBERTY LIBERTY LIBERTY` in a loop and crashed any process that imported it. Floating version ranges propagated the sabotage to thousands of build pipelines overnight ([Sharma, 2022](https://www.bleepingcomputer.com/news/security/dev-corrupts-npm-libs-colors-and-faker-breaking-thousands-of-apps/)).

Both incidents make the same point. **Floating versions outsource your release engineering to strangers.** A reproducible build pins every dependency, transitively, by exact version — and ideally by content hash.

---

## 11.4 The Build–Package–Deploy Pipeline

Most release problems become tractable once you separate three stages that are usually conflated.

| Stage | Input | Output | Defining property |
|---|---|---|---|
| **Build** | Source code + dependencies | Compiled artefact (binary, bundle, image layer) | Deterministic — same input, same output |
| **Package** | Artefact + metadata | Distributable (wheel, jar, deb, OCI image) | Immutable — never modified after publishing |
| **Deploy** | Distributable + config | Running instance | Reversible — can roll forward or back at will |

The cardinal rule is that *the same commit must produce a byte-identical artefact* — and that the artefact is then handled as a sealed object until it is running in production. The boundaries matter:

- **Build → Package.** Once built, an artefact is signed and given an immutable identifier (a version, a digest). Nobody edits it. If a fix is needed, you build a new artefact with a new identifier.
- **Package → Deploy.** Configuration is injected at deploy time, not baked in at build time. The same image runs in staging and production; only environment variables differ. This is the *twelve-factor* principle of strict separation between build and config ([Wiggins, 2011](https://12factor.net/)).

Teams that conflate the stages — for example, by having the deploy script pull the latest source and run `npm install` on the production host — lose all four release-engineering properties at once. The build is non-reproducible (dependencies float), traceability is weak (which `node_modules` actually shipped?), isolation fails (production state contaminates the build), and rollback is slow (you cannot un-install a half-applied `npm install`).

A clean pipeline looks like this:

```
[ commit abc1234 ]
        |
        v
   build  --->  artefact: api-server v1.5.0+sha.abc1234
        |
        v
  package --->  OCI image: registry.example.com/api@sha256:f3a2...
        |
        v
   deploy --->  running container in staging   (config: STAGING)
                running container in production (config: PROD)
```

Each arrow is a one-way door. Once an artefact is packaged, the only way to "change" it is to build a new one.

---

## 11.5 Reproducible Builds and the Software Supply Chain

Reproducibility is the foundation that everything else rests on. If you cannot rebuild last month's release from source, you cannot patch it without also forcing every customer onto your latest changes. If you cannot prove that the binary in production matches the source in your repository, you cannot say with confidence that the code reviewed by your team is the code your users are running.

### Lockfiles and Pinning

Every modern language ecosystem has a *lockfile* that records the exact version (and ideally the content hash) of every transitive dependency:

| Ecosystem | Manifest | Lockfile |
|---|---|---|
| JavaScript | `package.json` | `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` |
| Python | `pyproject.toml` | `poetry.lock`, `uv.lock`, `requirements.txt` (with hashes) |
| Rust | `Cargo.toml` | `Cargo.lock` |
| Go | `go.mod` | `go.sum` |
| Java | `pom.xml` / `build.gradle` | `pom.xml.lockfile` (less universal) |

Lockfiles must be committed to source control. A `.gitignore` that excludes `package-lock.json` is a release-engineering bug, not a stylistic preference. The lockfile is the record of *what was installed when this version was tested*; without it, every fresh checkout resolves dependencies anew, and "build the v1.4.2 tag" becomes a roll of the dice.

For container images, the equivalent pin is a **digest**, not a tag. `FROM node:20` is unpinned — the tag moves whenever the upstream maintainers rebuild. `FROM node:20.11.1-alpine3.19@sha256:e4ab...` is pinned: the image you build today is the image you build next year.

### SBOMs and Provenance

A *Software Bill of Materials* (SBOM) is a machine-readable inventory of everything inside an artefact: every library, every version, every licence. The two dominant formats are CycloneDX and SPDX. After the SolarWinds incident, US Executive Order 14028 (May 2021) made SBOMs a requirement for federal software suppliers ([White House, 2021](https://www.whitehouse.gov/briefing-room/presidential-actions/2021/05/12/executive-order-on-improving-the-nations-cybersecurity/)). The practical use is straightforward: when CVE-2024-3094 dropped (the xz-utils backdoor), teams with SBOMs ran one query — *do any of our images include xz-utils 5.6.0 or 5.6.1?* — and had an answer in minutes. Teams without SBOMs spent days grepping container images.

Tools like [Syft](https://github.com/anchore/syft) generate SBOMs from images; [Grype](https://github.com/anchore/grype) and [Trivy](https://aquasecurity.github.io/trivy/) cross-reference SBOMs against vulnerability databases.

### SLSA and Signing

The *Supply-chain Levels for Software Artefacts* (SLSA, pronounced "salsa") framework defines four levels of build integrity, from L1 (build is scripted) to L4 (two-person review, hermetic, reproducible) ([SLSA, 2023](https://slsa.dev/)). Most teams should aim for L2 — a hosted CI build that produces signed provenance metadata — and graduate to L3 once they have container signing in place.

Signing closes the last gap: the registry tells you the image's *digest*, but it does not tell you *who built it*. [Sigstore](https://www.sigstore.dev/) and `cosign` add a cryptographic signature to each image; deploy-time policy then refuses to run unsigned images. A team running `cosign verify` in its admission controller would have caught the SolarWinds backdoor at deploy time, because the malicious build was signed by the wrong key.

### Case: xz-utils, March 2024

For roughly two years, an attacker using the pseudonym "Jia Tan" contributed legitimately to the `xz-utils` compression library, gradually earning maintainer privileges. In February 2024 they shipped a patch hidden in test fixtures that injected a backdoor into the `liblzma` shared library — which is loaded by `sshd` on most Linux systems via `systemd`. The backdoor allowed remote code execution on any patched server. It was caught by Andres Freund, a Microsoft engineer who noticed `sshd` was 500 milliseconds slower than expected ([Freund, 2024](https://www.openwall.com/lists/oss-security/2024/03/29/4)).

The attack succeeded because the build environment itself was the target. The source code in Git looked clean; the distributed tarball — generated by the maintainer's local build — contained the backdoor. The patch shipped to Debian and Ubuntu's testing channels before the discovery. **A reproducible build directly from Git, ignoring the maintainer's tarball, would have produced a clean binary.** SLSA L3 — which requires hermetic builds from version-controlled source — is a direct response to this class of attack.

---

## 11.6 Packaging Formats — From Tarballs to OCI Images

The choice of packaging format determines what the artefact carries with it. The trend over the past four decades has been towards heavier packaging — each format includes more of its own dependencies and assumes less about the host.

| Format | Carries with it | Best for |
|---|---|---|
| **Source tarball** | Source code only | Open source distribution; rebuild on the target |
| **Language package** (wheel, jar, gem, npm) | Compiled artefact + language-specific metadata | Library distribution within a language ecosystem |
| **OS package** (deb, rpm) | Binary + system-level dependencies + install scripts | System tools tightly integrated with the host OS |
| **Static binary** (Go, Rust) | Self-contained executable | Single-file deployment without a runtime |
| **Container image** (OCI) | Binary + every userspace dependency + filesystem layout | Multi-language services with non-trivial dependencies |

The progression maps onto a single question: *what does the consumer have to install before this artefact will run?* A source tarball requires a full build toolchain. A wheel requires the right Python version. A deb requires the right OS family. A static binary requires the right CPU architecture. A container image requires only a kernel and a runtime.

Container images won the multi-service, multi-language race because they collapse the most difficult coordination problem in deployment — *getting the right libraries installed in the right place* — into a build artefact. The price is image size: a "minimal" Node.js image clocks in around 150 MB, and a careless one easily reaches 1 GB. The benefit is that the same image runs on any OCI-compliant runtime, anywhere.

The rest of this chapter focuses on container images, because that is where the bulk of new service deployment happens. The principles transfer: an image is a versioned, immutable, reproducible artefact, just like a wheel or a deb. The pipeline that produces it must satisfy the same four properties from §11.2.

---

## 11.7 Containerisation with Docker

Linux had everything needed for containers by 2008 — namespaces (process isolation), cgroups (resource limits), and a copy-on-write filesystem (image layers). What it lacked was a *format and a tool people would use*. Docker, released by Solomon Hykes in 2013, was that tool. The technical innovation was modest; the packaging innovation was enormous. Within five years, the format had been standardised by the Open Container Initiative (OCI) and adopted by every major cloud provider.

### What an Image Actually Is

An OCI image is three things in a tarball:

1. **A stack of filesystem layers** — each layer is a tarball of file additions or deletions, applied on top of the previous layer.
2. **A configuration object** — environment variables, the entrypoint command, the working directory, exposed ports.
3. **A manifest** — the list of layers and their content hashes, which together produce the image's digest.

Pulling `nginx:1.27.1` resolves the tag to a digest, downloads only the layers your host does not already have, and reconstructs the filesystem in an overlay mount. The image itself is read-only; the running container gets a thin writable layer on top.

### Anatomy of a Dockerfile

A Dockerfile is a recipe for the layer stack. Each instruction creates a new layer:

```dockerfile
# Pin the base image by digest, not just tag, for reproducibility.
FROM node:20.11.1-alpine3.19@sha256:e4ab... AS build

WORKDIR /app

# Copy dependency manifests first so dependency installation
# is cached separately from source code changes.
COPY package.json package-lock.json ./
RUN npm ci

# Now copy source and build.
COPY src ./src
RUN npm run build

# Multi-stage: a fresh, minimal final image carries only the build output.
FROM node:20.11.1-alpine3.19@sha256:e4ab...

WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules

# Run as non-root.
RUN addgroup -S app && adduser -S app -G app
USER app

EXPOSE 3000
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD wget -q -O- http://localhost:3000/healthz || exit 1
CMD ["node", "dist/server.js"]
```

The patterns in this file are doing real work:

- **Pinning by digest** survives upstream tag mutations (a `node:20` image rebuilt to fix a CVE quietly changes what your build produces).
- **Manifest copy before source copy** lets Docker cache the `npm ci` layer when only application code changes — turning a 90-second build into a 5-second one.
- **Multi-stage build** drops the build toolchain from the final image; the runtime image is megabytes smaller and has less attack surface.
- **Non-root user** means a container compromise does not immediately yield a root shell on the kernel.
- **Healthcheck** lets the orchestrator (Compose, in our case) tell whether the service is actually ready, not just whether the process is running.

### Image Hygiene

A Dockerfile that builds is not the same as a Dockerfile fit for production. The recurring pathologies:

- `:latest` base images — the build is no longer reproducible.
- Running as root — a privilege escalation vector for any container compromise.
- Secrets in build args — anyone who pulls the image can extract them with `docker history`.
- One-stage builds with the full toolchain in the final image — gigabytes of unnecessary attack surface.
- No `HEALTHCHECK` — the orchestrator can only tell that the process is alive, not that it works.

Tools like [hadolint](https://github.com/hadolint/hadolint) lint Dockerfiles against these patterns; running it in CI catches most of them automatically.

---

## 11.8 Beyond a Single Container — Docker Compose

A single container is rare in production. A real system has at minimum a frontend, a backend, and a datastore. Each has different lifecycles, different scaling needs, and different failure modes. Running `docker run` three times by hand reproduces nothing — there is no record of which images were used, which networks they shared, or which volumes mounted where.

*Docker Compose* solves this by describing the topology in a single YAML file. A Compose file is to a multi-container application what a `Dockerfile` is to a single image: a declarative, version-controlled specification that anyone with Docker installed can run identically.

The unit of Compose is the *service*. A service has an image (or a `build:` directive that produces one), environment variables, ports, volumes, and dependencies on other services. Compose creates a private network so services can address each other by service name (`postgres`, `api`), wires up the volumes, and starts everything in dependency order.

Compose is the *right tool* for three contexts:

1. **Local development** — every contributor gets the same database, the same API, the same web frontend, with one command (`docker compose up`).
2. **Integration testing in CI** — spin up the full stack, run end-to-end tests, tear it down.
3. **Small production deployments** — a single host running a multi-container application, where the operational simplicity of "one Compose file, one VM" outweighs the cost of running it that way.

For deployments that need automatic scaling across many hosts, Compose is no longer the right answer. Those deployments need an orchestrator with scheduling and failover; Compose deliberately stops at "describe the topology, run it on one host." This chapter stops where Compose stops.

---

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

## 11.10 Deployment Strategies and Risk

A working artefact and a working topology still need to *replace* the version that is running. The strategy you choose for that replacement determines the blast radius when something is wrong.

| Strategy | Mechanism | Downtime | Rollback speed | Risk profile |
|---|---|---|---|---|
| **Recreate** | Stop old, start new | Yes (seconds to minutes) | Slow — restart old | Internal tools, off-hours |
| **Rolling** | Replace instances one at a time | None | Medium — roll back one at a time | Default for most stateless services |
| **Blue-Green** | Run two full environments; swap traffic | None | Instant — swap back | High-stakes, infrequent releases |
| **Canary** | Send 1% / 5% / 25% of traffic to the new version | None | Instant for affected slice | Risky changes, large user base |
| **Feature flag** | Deploy code dark; enable per-user at runtime | None | Instant per-user | Decoupling deploy from release |

Three observations matter more than the table itself.

**Deployment is not the same as release.** A deployment ships code to production. A release exposes that code to users. Feature flags decouple the two: ship the code dark, validate that nothing is on fire, then turn it on for 1% of users, then 10%, then everyone. Most outages from "the deploy" are actually outages from "the release" — and a flag flip is an order of magnitude faster to revert than a redeploy.

**Canaries catch what staging does not.** Staging environments have synthetic traffic, a single test user, and a snapshot of production data from last Tuesday. Real users are weirder. A 1% canary exposes the new version to 1% of *real* traffic — the long-tail edge cases, the unexpected user-agent strings, the malformed Unicode in someone's display name. CrowdStrike's outage would have been an 85,000-host incident with a 1% canary instead of an 8.5-million-host incident.

**Rollback is a feature, not an afterthought.** If your deploy process cannot revert to the previous version in under five minutes, you do not have a deploy process — you have a one-way door. The first deploy of any new system should be followed immediately by a *rollback drill*: deliberately deploy a known-broken version, then revert. If the drill takes an hour, fix the process before shipping anything that matters.

---

## 11.11 Production Readiness — The Last Mile

A service that survives its first deploy is not yet production-ready. Production readiness is a checklist of operational properties that determine whether the service can be debugged, monitored, and recovered when (not if) something goes wrong.

| Property | What it means | Failure mode without it |
|---|---|---|
| **Liveness probe** | Endpoint that says "the process is alive" | Hung process holds traffic; orchestrator does not restart it |
| **Readiness probe** | Endpoint that says "ready to serve" | New container takes traffic before warming caches; first 100 requests fail |
| **Structured logging** | Logs as JSON with consistent fields | An incident at 2 a.m. requires `grep`-and-pray |
| **Metrics** | Counters, gauges, histograms (RED/USE) | "Is the service slow?" requires running ad-hoc queries |
| **Graceful shutdown** | Drain in-flight requests on SIGTERM | Every deploy drops a few hundred requests |
| **Secrets management** | Secrets injected at runtime, not in images | A leaked image leaks the database password |
| **Configuration drift detection** | Production config matches what is checked in | An emergency edit on the host is forgotten and re-broken on next deploy |

Two of these are worth singling out. The first is **graceful shutdown.** When the orchestrator wants to stop a container, it sends SIGTERM, waits a grace period (usually 10–30 seconds), and then sends SIGKILL. A correctly written service catches SIGTERM, stops accepting new connections, finishes the in-flight requests, closes its database connections, and exits. A service that ignores SIGTERM until SIGKILL drops every in-flight request, every deploy. Web frameworks make this surprisingly easy to get wrong; FastAPI's lifespan handlers and Express's `server.close()` both need to be wired up explicitly.

The second is **structured logging.** A log line of the form

```
2026-05-06T14:32:01Z ERROR [api.handlers.checkout] order=78d3a stage=charge gateway=stripe latency_ms=4321 error="declined: insufficient_funds"
```

is dramatically more useful than

```
ERROR: payment failed for order
```

The first can be queried, aggregated, and joined against tracing data. The second is a guess at what was happening.

**Every item on this list is a place where AI agents will silently leave gaps if you do not check.** Agents generate "complete" services that have a `/healthz` endpoint returning `200` regardless of internal state, log to stdout with `print()`, and ignore SIGTERM. The code compiles, the tests pass, the deploy succeeds — and the first incident reveals what was missing.

---

## 11.12 AI-Native Considerations — Agents That Package and Ship

Coding agents are good at producing release infrastructure that looks right. They are less good at producing release infrastructure that *is* right. The gap matters because release infrastructure is the last line of defence between a defect and a customer.

### Where Agents Reliably Mislead

Six recurring failure patterns in agent-generated packaging:

1. **Floating base images.** `FROM node:20` instead of `FROM node:20.11.1-alpine3.19@sha256:...`. The Dockerfile builds today; in three months the same Dockerfile produces a different image and your reproducibility is gone.
2. **Root user by default.** No `USER` directive, so the container runs as root. A vulnerability in the application becomes a kernel-adjacent compromise.
3. **Secrets in environment variables and `.env`.** The agent solves "the database needs a password" by putting the password in `.env` — and `.env` ends up committed because the agent did not also update `.gitignore`.
4. **Missing health checks.** Compose `depends_on` without `condition: service_healthy`; Dockerfiles without `HEALTHCHECK`; the orchestrator cannot tell ready from broken.
5. **One-stage builds.** The full build toolchain ships in the final image. A Node.js service that should be 150 MB is 1.2 GB and ships `gcc`, `python3`, and the build user's name.
6. **Generated CI manifests with broad permissions.** GitHub Actions workflows with `permissions: write-all` and `pull_request_target: ` triggers, which are textbook supply-chain risk. A 2023 Dependabot study found that more than a third of agent-suggested workflows had at least one of these patterns.

### Three Guardrails

Treat these as non-negotiable. Each catches a category that agents reliably miss.

- **Pinning is a contract.** The agent's Dockerfiles, lockfiles, and Compose files pass review only if every dependency is pinned by version *and* — for container images — by digest. CI fails the build if `:latest` or unpinned `node:20` appears anywhere.
- **Policy as code.** Run `hadolint` on every Dockerfile, `trivy image` on every produced image, and `checkov` or `conftest` on every Compose file, in CI. The agent does not get to decide what is acceptable; the policy file does. The cost is a few seconds per build; the saving is roughly the cost of one avoided incident per quarter.
- **A human-reviewed release manifest.** The boundary between "agent-written" and "production-shipped" is a human signing off on what is being released. The release manifest is short — version, commit, image digest, SBOM, change summary — and it is reviewed by a person, not a bot. This is the same pattern as code review, applied to the artefact rather than to the source.

### Why This Matters More Than It Used To

A human engineer writing a Dockerfile by hand produces one Dockerfile a week. A coding agent can produce twenty in a morning. The probability that *one of them* contains a release-engineering mistake — an unpinned base image, a missed health check, a leaked secret — does not stay at 10% per Dockerfile when the volume is twentyfold. The aggregate exposure scales linearly.

The CrowdStrike incident took down 8.5 million hosts because *one* configuration file was malformed and *one* release pipeline pushed it everywhere. The defect rate per file did not need to be high. It needed to be non-zero and uncaught. Agentic codebases do not lower the defect rate; they raise the volume. Release-engineering rigour is what keeps the resulting incident rate flat instead of climbing in proportion to the agent's output.

---

## 11.13 Key Takeaways

1. **Production correctness is a property of the pipeline, not the code.** The CrowdStrike, Knight Capital, and SolarWinds incidents were all *correct code, broken delivery*. Closing the production gap is the job of release engineering.

2. **A version is a contract.** SemVer for libraries, CalVer for applications. ZeroVer, marketing versions, and floating tags break the contract and force consumers to pin defensively.

3. **Build, package, deploy are three distinct stages.** Conflating them — running `npm install` on the production host, editing config in place — destroys reproducibility, traceability, isolation, and reversibility in one move.

4. **Pin everything.** Lockfiles for libraries, digests for container images. Floating versions outsource your release engineering to strangers, as left-pad and colors.js made expensive to forget.

5. **An SBOM is a one-query answer to the next supply-chain incident.** Generate one on every build; cross-reference it against vulnerability databases in CI. xz-utils-shaped attacks become a Trivy report instead of a weekend.

6. **Containers are the dominant packaging format because they collapse dependency coordination into a build artefact.** That benefit is conditional on disciplined Dockerfile authorship — pinned bases, multi-stage builds, non-root users, health checks, signed images.

7. **Compose is for one host; that is enough for a great deal of production.** Compose buys you reproducible local development, integration testing, and small-scale production deployment. Larger deployments need an orchestrator; the principles of pinning, healthchecks, and immutable artefacts transfer unchanged.

8. **Deployment strategy determines the blast radius.** Rolling deploys are the default; canaries catch what staging does not; feature flags decouple deployment from release. CrowdStrike was an incident-of-staging-strategy as much as it was an incident-of-code.

9. **Production readiness is a checklist, not a vibe.** Liveness, readiness, structured logging, metrics, graceful shutdown, secrets management. Each item is a question an incident will eventually ask; the time to answer it is before the incident.

10. **AI-generated release infrastructure is the supply-chain risk of the next decade.** Pin, scan, sign, and require a human-reviewed release manifest. Agents make production-grade pipelines cheap; they do not make them free.

---

## Review Questions

1. Your team adopts a coding agent that produces a Dockerfile for a new Python service. The Dockerfile uses `FROM python:3.12`, runs `pip install -r requirements.txt` (no lockfile), copies the source, and ends with `CMD ["python", "main.py"]`. Identify five release-engineering defects in this Dockerfile, and explain the production failure mode each one will eventually cause.

2. A library you maintain ships a "patch" release that renames a public function. Within 48 hours, three downstream projects file bug reports because their builds are broken. Using SemVer's contract, explain (a) what rule was violated, (b) what the correct version number should have been, and (c) what your release pipeline could have done to catch the violation before publishing.

3. A teammate proposes deploying to production by SSH-ing to the host and running `git pull && docker compose up -d --build`. The argument is "it is simple, and we already trust the source repository." Identify which of the four release-engineering properties (reproducibility, traceability, isolation, reversibility) this approach loses, and describe a specific failure scenario for each.

4. The CrowdStrike incident pushed a malformed configuration file to all customers simultaneously. Design a deployment strategy that would have limited the blast radius to under 100,000 hosts, including what you would canary on, how long you would wait at each stage, and what signal would trigger a rollback. Be specific about the metrics you would watch.

5. An agent generates a Compose file for a `web + api + db` stack. The file omits health checks, uses `depends_on: [db]` (no condition), publishes `5432:5432` for the database, and stores the database password in `.env`, which has been committed. Write a code review comment for each defect that explains the *production failure mode*, not just the rule violated.

6. A vulnerability is announced in a transitive dependency three layers deep in your service. Compare two scenarios: (a) your team has pinned dependencies, generates SBOMs, and signs images; (b) your team uses floating versions, has no SBOM, and pulls images by tag. Walk through the first hour of incident response in each scenario and quantify, roughly, how long it takes to answer the question *are we vulnerable?*.

---

## Further Reading

- Adams, B., & van der Hoek, A. (2016). *Modern Release Engineering in a Nutshell — Why Researchers Should Care*. IEEE SANER. [ieeexplore.ieee.org/document/7476770](https://ieeexplore.ieee.org/document/7476770)
- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (2016). *Site Reliability Engineering: How Google Runs Production Systems*. O'Reilly. [sre.google/sre-book/release-engineering/](https://sre.google/sre-book/release-engineering/)
- Wiggins, A. (2011). *The Twelve-Factor App*. [12factor.net](https://12factor.net/)
- Preston-Werner, T. (2013). *Semantic Versioning 2.0.0*. [semver.org](https://semver.org/spec/v2.0.0.html)
- Open Container Initiative. (2017). *OCI Image and Runtime Specifications*. [opencontainers.org](https://opencontainers.org/)
- SLSA Authors. (2023). *Supply-chain Levels for Software Artefacts*. [slsa.dev](https://slsa.dev/)
- White House. (2021). *Executive Order 14028 on Improving the Nation's Cybersecurity*. [whitehouse.gov](https://www.whitehouse.gov/briefing-room/presidential-actions/2021/05/12/executive-order-on-improving-the-nations-cybersecurity/)
- Freund, A. (2024). *Backdoor in upstream xz/liblzma leading to ssh server compromise*. oss-security mailing list. [openwall.com/lists/oss-security/2024/03/29/4](https://www.openwall.com/lists/oss-security/2024/03/29/4)
- Docker Inc. (2024). *Compose Specification*. [docs.docker.com/compose/compose-file/](https://docs.docker.com/compose/compose-file/)
