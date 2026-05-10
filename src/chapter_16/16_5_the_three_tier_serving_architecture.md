## 16.5 The Three-Tier Serving Architecture

---

A production ML application is not a monolithic system that combines the user interface, application logic, and model inference in a single process. It is a layered architecture in which each tier has a single, well-defined responsibility. Violating this separation — putting model loading code in the frontend, or business logic in the serving API — produces a system that is difficult to scale, test, update, and monitor independently.

The three-tier architecture separates concerns into a frontend tier, a backend API tier, and a model serving tier.

### 16.5.1 The Frontend Tier

The frontend is the interface through which users or client applications interact with the ML system. Its responsibility is presentation and interaction: collecting inputs, displaying results, handling errors, and providing contextual information that helps users interpret the model's output. It has no knowledge of how predictions are generated, which model version is in use, or how the backend is deployed.

For the ChestScan application, the frontend is a Streamlit application. A radiologist uploads a chest X-ray, clicks a button, and sees a diagnosis with a confidence score and a Grad-CAM heatmap. The Streamlit application sends an HTTP request to the FastAPI backend and displays whatever the backend returns. If the backend is unavailable, the frontend displays an error. If the model version changes, the frontend displays the new results with no code change required.

The strict separation between frontend and backend enables independent deployment and scaling. The frontend can be updated — with a new layout, additional context for the user, or support for a different file format — without any change to the backend. The backend can be updated — with a new model version, a different preprocessing pipeline, or improved error handling — without any change to the frontend.

### 16.5.2 The Backend API Tier

The backend API is the bridge between the frontend and the model. Its responsibilities are input validation, model invocation, output formatting, prediction logging, and error handling. It knows about the model and about the contract with the frontend; it knows nothing about how the model was trained or how the frontend renders its outputs.

For the ChestScan application, the backend is a FastAPI application exposing three endpoints: a health check, a prediction endpoint, and an explanation endpoint. The health check confirms that the model is loaded and the service is ready. The prediction endpoint accepts a chest X-ray image, validates it, applies the preprocessing transforms, invokes the model, and returns the class, confidence, and class probabilities. The explanation endpoint applies Grad-CAM to the same image and returns the heatmap overlay as a PNG.

The backend logs each prediction to the MLflow tracking server — the prediction ID, the predicted class, the confidence, and the individual class probabilities. This logging is the bridge between serving and monitoring: without it, the monitoring system has no data to analyse.

### 16.5.3 The Model Serving Tier

In the ChestScan three-tier architecture, the model serving tier is the model registry from which the backend loads the model at startup. In larger-scale systems, this tier is a dedicated model serving platform: TorchServe, TensorFlow Serving, NVIDIA Triton Inference Server, or a managed service such as AWS SageMaker or Google Vertex AI.

Dedicated model serving platforms provide capabilities beyond what a general-purpose web framework offers: batching of concurrent inference requests to improve GPU utilisation, dynamic batching that accumulates requests until a batch size threshold is reached or a timeout expires, model version management with automatic routing between versions, and specialised hardware scheduling. For applications processing large volumes of images — thousands per second at inference time — these capabilities are necessary. For applications with moderate throughput requirements, loading the model in the API process is simpler and sufficient.

The key engineering principle is the same at either scale: the model is a resource loaded once at startup, shared across requests, and updated without restarting the serving process.

---
