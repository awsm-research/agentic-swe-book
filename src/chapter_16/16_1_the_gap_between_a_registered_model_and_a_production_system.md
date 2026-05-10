## 16.1 The Gap Between a Registered Model and a Production System

---

Completing a training run and registering the resulting model in a model registry is a significant engineering achievement. It is also approximately the halfway point in building a production ML application. The artefact sitting in the registry — weights, a serialised computation graph, preprocessing configuration, evaluation metrics — is necessary but not sufficient. It cannot receive HTTP requests. It has no knowledge of the environment it will run in. It cannot detect when the inputs it is receiving in production have drifted away from the distribution it was trained on. It cannot update itself when a better version is registered. These capabilities must be engineered separately, and engineering them well requires confronting problems that have no equivalent in standard software development.

The gap is structural. A trained model is a mathematical function: given an input tensor, produce an output tensor. A production system is an infrastructure: accept requests from clients, validate inputs, invoke the function, log the results, expose health information, recover from failures, update without downtime, and raise an alarm when the function's behaviour suggests it is no longer trustworthy. The engineering discipline concerned with closing this gap is machine learning operations — MLOps — and the conceptual territory it covers is the subject of this chapter.

### 16.1.1 Why ML Deployment Is Not Trivial

Deploying a conventional software application involves packaging code, configuring dependencies, and provisioning infrastructure. These challenges are well-understood and well-tooled. ML deployment involves all of these, plus a set of complications unique to data-dependent systems.

**Model size.** A pretrained deep learning model typically ranges from hundreds of megabytes to tens of gigabytes. Loading model weights on every request is computationally prohibitive — the model must be loaded once at startup, held in memory (or GPU VRAM), and reused across requests. This singleton loading pattern has no direct counterpart in conventional web services, where stateless request handlers are the norm.

**Hardware specialisation.** Training and inference at scale require GPU acceleration. GPUs are not fungible with CPUs in the same way that an additional application server pod is. Provisioning GPU infrastructure, allocating it correctly between services, and ensuring that the model actually runs on the hardware it was provisioned on requires explicit engineering attention. A model trained on a GPU will run on a CPU, but at a fraction of the throughput — and a serving system that silently falls back to CPU inference may appear healthy while delivering unacceptable latency.

**Warm-up latency.** The first inference request processed by a newly loaded model is typically slower than subsequent requests, due to JIT compilation, kernel caching, and memory allocation. This warm-up effect means that a newly deployed model may produce high-latency responses for the first requests it handles, which can violate service-level objectives if load balancers route traffic before the service has warmed up. Health check endpoints that report readiness only after a warm-up inference has completed address this problem.

**Preprocessing contract.** The model was trained on data that was transformed in a specific way: resized to specific dimensions, normalised with specific parameters, converted to a specific data type. These transformations must be replicated exactly at serving time. Any deviation — a slightly different resize interpolation method, a normalisation applied in the wrong order — produces a silently incorrect result. The model does not raise an exception. It processes the malformed input and produces a prediction that appears structurally valid but is generated from a distribution the model was not trained on.

**Silent failure.** Standard software fails loudly: an exception is raised, an error is returned, a log entry is written. A misconfigured ML serving system fails silently: it produces predictions, logs them, and reports healthy — while the predictions are meaningless because the input preprocessing is wrong, the wrong model version was loaded, or the model's training distribution no longer matches production traffic. Silent failure is the defining hazard of ML deployment, and addressing it requires monitoring infrastructure that standard application observability tooling does not provide.

### 16.1.2 The Three Questions Every Deployment Must Answer

Before a trained model can be deployed to production, three questions must have engineering answers — not assumptions.

**How will the model be loaded?** From the filesystem, from an object store, or from a model registry? Baking model weights into a container image conflates the deployment artefact with the model version, requiring a full image rebuild and redeploy whenever the model is updated. Loading from a registry at startup decouples these concerns: the container defines the serving environment, the registry defines the model version, and updating one does not require changing the other.

**How will the model be updated?** In a live system, model updates must happen without service interruption. The alias pattern — referencing a model by a role name such as `@champion` rather than a version number — is the mechanism that enables this. The serving code loads whatever model is currently assigned the `@champion` alias. Promoting a new model version to that alias is an atomic registry operation that takes effect on the next model load, without any change to the serving infrastructure.

**How will you know when the model is behaving incorrectly?** This requires a monitoring plan before deployment, not after the first incident. The monitoring plan must specify what signals will be collected, what thresholds will trigger an alert, and what action will be taken in response. A monitoring plan created in response to an incident is a post-mortem recommendation, not a deployment gate.

---
