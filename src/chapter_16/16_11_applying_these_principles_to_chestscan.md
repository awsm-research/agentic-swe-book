## 16.11 Applying These Principles to ChestScan

---

The principles covered in this chapter are not abstract. Each one has a direct application in the ChestScan pneumonia detection system, and the architecture choices made in Chapter 15 are the practical implementations of the conceptual positions taken here.

### 16.11.1 Serving Architecture

ChestScan is an online inference system. Chest X-rays are uploaded by radiologists at the moment they need a second opinion, and the diagnosis must be available within seconds. A batch inference system that pre-computes diagnoses overnight is not appropriate for this use case. The three-tier architecture — Streamlit frontend, FastAPI backend, MLflow model registry — enforces the separation of concerns that allows each component to evolve independently.

The singleton model loader in the FastAPI backend addresses the model size and warm-up latency challenges described in section 16.1.1: the model is loaded once at startup, held in memory, and reused across requests. The health endpoint reports model readiness, preventing load balancers from routing traffic before the model is loaded.

### 16.11.2 Train/Serve Skew Prevention

The shared `transforms.py` module is the implementation of the shared module pattern from section 16.3.2. The training pipeline and the FastAPI backend import the same function from the same file. The file is physically copied into the serving container as part of the Docker build, ensuring that the serving code cannot silently diverge from the training code's preprocessing.

### 16.11.3 Zero-Downtime Updates

The FastAPI backend loads the model by the `@champion` alias. When a new model version is registered and promoted to `@champion` in the MLflow registry, the change takes effect on the backend's next startup — or immediately in a system that implements dynamic model reloading. No code change, no container rebuild, and no service interruption is required.

### 16.11.4 Production Monitoring

Each prediction logged by the FastAPI backend is written to the `production-predictions` MLflow experiment with the prediction ID, predicted class, confidence, and individual class probabilities. The drift detection script reads these records, computes PSI on the prediction class distribution and the confidence distribution relative to training baselines, and exits with a non-zero code if PSI exceeds 0.2 — triggering a notification and initiating a retraining evaluation.

The training class distribution of the Kaggle Chest X-Ray dataset (73% pneumonia, 27% normal; approximately 47.5% bacterial and 25.5% viral among the pneumonia cases) serves as the reference distribution. A production deployment at a different clinical centre, serving a different patient population, should not necessarily expect to match this baseline. The reference distribution should be updated to reflect the deployment population — which requires establishing a baseline from the first weeks of production data rather than assuming the training set prevalence applies universally.

This is a genuine limitation of the ChestScan monitoring setup as described: a deployment that differs systematically from the Guangzhou Women and Children's Medical Centre paediatric population will generate persistent PSI alerts that reflect population difference rather than model degradation. Establishing a deployment-specific baseline from the first month of production data is the correct long-term approach.

---
