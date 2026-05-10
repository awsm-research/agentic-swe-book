## 16.4 Containerisation for ML Serving

---

The argument for containerising ML serving systems is straightforward: a container packages the application code, its dependencies, and its configuration into a single artefact that runs identically in development, staging, and production. The "works on my machine" failure mode is eliminated by definition, because the machine is specified as part of the artefact.

ML serving systems have specific containerisation requirements that differ from those of standard web applications.

### 16.4.1 Model Weights Do Not Belong in the Image

The most common containerisation mistake for ML serving is baking model weights into the container image. This mistake is attractive because it simplifies startup — the model is present on disk the moment the container starts, with no download required. It is a serious architectural error for three reasons.

First, it conflates the deployment artefact with the model version. Updating the model requires building a new image, pushing it to a registry, and redeploying the container — a process that takes minutes and introduces downtime risk. With the model loaded from a model registry at startup, updating the model is an atomic registry operation that takes milliseconds.

Second, it breaks auditability. A model baked into an image cannot be traced back to the training run that produced it unless that traceability was explicitly engineered — which, in practice, it almost never is. A model loaded from the MLflow registry at startup is traced automatically: the registry version is returned by the health endpoint and logged with every prediction.

Third, it prevents zero-downtime updates. If the model is in the image, every model update requires a full container replacement with the associated operational risk. If the model is loaded from the registry, the serving alias can be updated and the change takes effect on the next startup without any change to the running container.

### 16.4.2 GPU Access in Containers

Container runtime environments do not expose GPU hardware by default. To use a GPU from within a container, the host must have the appropriate drivers installed, the container runtime must be configured to allow GPU access, and the container image must include the correct CUDA libraries. These three requirements must be satisfied simultaneously — a mismatch between any two produces a container that believes it has GPU access but silently falls back to CPU, or one that fails to start entirely.

For CPU-only serving — appropriate for models with moderate inference costs and moderate throughput requirements — a standard Python base image is sufficient. For GPU serving, the correct base image is a CUDA-enabled image that pins the CUDA version to match the host driver. Unpinned CUDA images that track the latest CUDA version will break when the host driver version does not support that release.

### 16.4.3 The Multi-Stage Build

A multi-stage Docker build separates the build environment from the runtime environment. The build stage installs compilers, build tools, and development headers needed to compile Python extension modules. The runtime stage copies only the installed packages and application code — no build tools, no development headers, no caches. The result is a smaller image with a reduced attack surface.

This separation matters for ML serving specifically because scientific Python packages — NumPy, PyTorch, OpenCV, scikit-learn — often require C and C++ compilation during installation. Including `gcc` and `g++` in the runtime image only because they were needed during installation is a common and avoidable error. The multi-stage pattern eliminates it by design.

### 16.4.4 Security Baseline

Running production services as root is indefensible. A container that runs as root gives any process within it the same privileges as root on the host system if a container escape vulnerability is exploited. Creating a non-root user and switching to it before the application starts is a minimal addition to the Dockerfile and eliminates an entire class of privilege escalation risk.

Pinning the base image to a specific version — `python:3.11-slim` rather than `python:latest` — ensures that the image does not change unexpectedly when the base image is updated. Unpinned images introduce a class of non-deterministic build failure where the same Dockerfile produces different images at different times, violating the reproducibility guarantee that containerisation is supposed to provide.

---
