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
