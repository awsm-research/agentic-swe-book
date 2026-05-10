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
