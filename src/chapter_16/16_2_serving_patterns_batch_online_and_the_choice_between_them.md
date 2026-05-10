## 16.2 Serving Patterns: Batch, Online, and the Choice Between Them

---

The first architectural decision in building a model serving system is whether predictions will be generated on demand or in advance. This choice — batch versus online inference — determines the infrastructure required, the latency characteristics delivered, and the failure modes the system must manage.

### 16.2.1 Batch Inference

In batch inference, a pipeline reads a collection of inputs from a data store, generates predictions for all of them, and writes the results back. The pipeline runs on a schedule — hourly, daily, or triggered by the availability of new data. No user or downstream system waits for the pipeline to complete a prediction; the results are pre-computed and stored.

Batch inference is appropriate when predictions are needed at lower frequency than inputs arrive, when the cost of individual predictions is high, when predictions are consumed in bulk (reports, ranked lists, population-level scoring), and when a delay between input and prediction is acceptable. A system that scores all loan applications received in a day, generates a daily ranked list of content recommendations, or pre-computes risk scores for an entire patient cohort is a batch inference system.

The engineering characteristics of batch inference are tractable. The pipeline is a standard ETL job. Failures can be retried. Resource allocation is predictable. The model can be loaded once per pipeline run rather than kept in memory continuously. Scaling is achieved by parallelising across inputs.

### 16.2.2 Online Inference

In online inference, a serving API receives a request containing a single input (or a small batch), generates a prediction, and returns the result synchronously within a latency budget. The user or downstream system waits for the response.

Online inference is appropriate when predictions must be generated in real time, when inputs arrive one at a time or in small batches, when the latency of the prediction is part of the user experience, and when the set of possible inputs cannot be pre-computed. A system that classifies a chest X-ray at the moment it is uploaded, evaluates a credit card transaction as it is submitted, or generates a recommendation when a user opens a page is an online inference system.

The engineering characteristics of online inference are more demanding. The model must be kept in memory and ready to respond. Latency must be measured and guaranteed. Concurrency must be handled correctly — multiple requests arriving simultaneously must not interfere with each other. The serving API must implement input validation, because a malformed request that reaches the model can produce a misleading result rather than an error. Health checks must accurately reflect whether the model is loaded and responding correctly.

### 16.2.3 Synchronous vs. Asynchronous Online Inference

Within online inference, a further distinction applies: whether the client waits for the prediction (synchronous) or submits the request and retrieves the result later (asynchronous).

Synchronous inference is the correct pattern for most interactive applications. The user uploads an image and expects a result. A downstream service calls the prediction API and needs the result to complete its own response. The latency budget is seconds or milliseconds. This is the pattern used in the ChestScan application: the Streamlit frontend submits a chest X-ray to the FastAPI backend via a synchronous HTTP POST and displays the result when the response arrives.

Asynchronous inference is appropriate when the prediction is computationally expensive, when the result is not needed immediately, or when throughput is more important than individual request latency. A request is submitted to a queue, a worker processes it, and the result is stored for later retrieval. This pattern is common in video processing, large document analysis, and any pipeline where generating a single prediction takes minutes rather than seconds.

### 16.2.4 The REST API as the Standard Interface

For online inference in production systems, the REST API is the standard interface between the serving system and its consumers. A REST API provides a language-agnostic interface that any client — a web browser, a mobile application, another backend service — can call using standard HTTP. It enforces a clear boundary between the model and its consumers: the API contract specifies what inputs are accepted and what outputs are returned, and the serving code is free to change the underlying model, preprocessing, and infrastructure without breaking clients as long as the contract is honoured.

The minimal REST API for a production ML serving system exposes at least two endpoints: a health endpoint that reports whether the service is ready to serve requests, and a prediction endpoint that accepts an input and returns a prediction. The health endpoint is not optional — it is the mechanism by which load balancers, orchestrators, and health check pipelines determine whether the service is functioning correctly.

---
