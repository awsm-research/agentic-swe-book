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
