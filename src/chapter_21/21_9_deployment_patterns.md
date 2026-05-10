## 21.9 Deployment Patterns

---

LLM applications have distinct deployment characteristics that make the choice between serverless and always-on infrastructure more consequential than it is for conventional web services.

### 21.9.1 Serverless Deployment

Serverless platforms — AWS Lambda, Google Cloud Run, Azure Functions — execute code in response to events, scaling automatically and charging only for actual compute consumed. They are appealing for LLM applications because they handle traffic spikes without manual scaling and reduce costs during idle periods.

The critical problem for LLM applications is the **cold start**. A serverless function that has not received traffic recently must be initialised before it can handle a request. For a conventional web service, a cold start might add 100–500 milliseconds. For an LLM application that must load model weights, initialise connection pools, pre-load embedding models, and warm guardrail classifiers, a cold start may add 5–15 seconds. For a user waiting for a chatbot response, this is catastrophic.

Streaming compounds the cold-start problem. Many serverless platforms impose maximum execution time limits — 15 seconds for AWS Lambda by default, 60 minutes with extended settings. A streaming response for a complex query may approach or exceed default limits. Serving streaming LLM responses from Lambda requires careful configuration of timeouts and response streaming mode, which AWS added to Lambda only in 2023.

Serverless is appropriate for LLM applications where:

- Traffic is highly variable and unpredictable
- Latency requirements can absorb occasional cold-start overhead
- The application does not use streaming, or streaming is handled through a separate always-on component
- Workloads are asynchronous (batch processing, webhook handlers, nightly pipelines)

### 21.9.2 Always-On Deployment

Always-on infrastructure — Kubernetes clusters, dedicated container services, traditional virtual machines — maintains persistent processes that are ready to handle requests at any time. Cold starts are eliminated because the application is always warm. Streaming is handled naturally because connections persist. Latency is predictable.

The cost model inverts. Always-on infrastructure incurs cost whether or not it is serving requests. A cluster provisioned for peak load spends most of its time underutilised, paying for idle capacity. Cluster autoscaling reduces this waste but reintroduces a form of the cold-start problem as new nodes are provisioned during traffic spikes.

For most production conversational AI applications serving interactive users, always-on deployment is the correct default. The latency predictability and streaming compatibility outweigh the cost premium, particularly when horizontal autoscaling is properly configured to handle variable load without over-provisioning.

### 21.9.3 Hybrid Patterns

Many mature LLM serving architectures use a hybrid approach: an always-on core handles interactive, latency-sensitive requests while serverless functions handle asynchronous workloads. The LiteLLM gateway runs as an always-on service; batch processing pipelines run as serverless jobs. The gateway's fallback routing can route synchronous overflow traffic to alternative providers during peak periods rather than provisioning excess always-on capacity for rare spikes.

Container orchestration platforms, particularly Kubernetes, have emerged as the preferred infrastructure for always-on LLM serving. Kubernetes provides the horizontal scaling, health checking, and deployment management needed to operate a production serving stack reliably. Its ecosystem of tools — Horizontal Pod Autoscaler, Vertical Pod Autoscaler, and cluster autoscalers for major cloud providers — allows capacity to track demand reasonably well, reducing idle waste while maintaining readiness for load spikes.

---
