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
