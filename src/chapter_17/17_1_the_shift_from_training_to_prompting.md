## 17.1 The Shift from Training to Prompting

---

Chapter 13 introduced Software 3.0 as the generation where the prompt decides. That framing captures something technically precise: in Software 1.0, a developer writes logic; in Software 2.0, an optimiser learns logic from data; in Software 3.0, a developer writes natural language instructions and a pre-trained foundation model executes them. The shift reorganises the entire relationship between the engineer and the system's behaviour.

In Software 2.0, the primary engineering artefact is a trained model. The team controls the training data, the architecture, the objective function, and the hyperparameters. If the model behaves incorrectly, the team retrains it with better data or a different objective. The model is owned in a meaningful engineering sense: its weights are the team's product, and changing its behaviour is a matter of changing the training process.

In Software 3.0, the primary engineering artefact is a prompt — or more precisely, a prompt layer that wraps a foundation model the team does not own and did not train. The model's weights are the provider's product. The team cannot change them, cannot inspect them, and often cannot predict exactly how they will respond to edge cases. What the team controls is the text placed in front of the model: the system prompt, the user's input, any retrieved context, and the conversation history. The engineering challenge shifts from "how do we train a model that behaves correctly?" to "how do we design a context that reliably elicits correct behaviour from a model we cannot control?"

This shift has consequences that engineers trained in Software 1.0 and 2.0 paradigms consistently underestimate. A Software 1.0 function is deterministic: the same input always produces the same output. A Software 2.0 model has probabilistic outputs but stable weights — run the same input through the same model and you get the same distribution. A Software 3.0 system is probabilistic at the model level, stateless by default, sensitive to context construction, and subject to behaviour changes whenever the model provider pushes an update to the underlying weights — even if your application code does not change. Every architectural decision must account for this structural property.

The engineer's job in Software 3.0 is therefore not to build a model. It is to build a system that reliably produces correct, safe, and useful outputs by constructing the right context for a model it does not control, while managing cost, latency, and failure modes that have no direct analogue in previous engineering generations.

---
