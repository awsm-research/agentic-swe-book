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
