# Chapter 16: Model Serving, Deployment, and Production Monitoring

> *"The difference between a model and a product is everything that happens after training ends."*
> — Kla Tantithamthavorn

---

In July 2015, Google Photos launched its automatic tagging feature with considerable confidence. Within days, a Black software developer discovered that the system had labelled photographs of him and a friend as "gorillas." Google's response was to delete the label category entirely — not to fix the underlying model. Three years later, a reporter tested the service again and found that "gorilla," "chimp," and "chimpanzee" remained disabled as labels, while "poodle" and "hamster" worked correctly ([Simonite, 2018](https://www.wired.com/story/when-it-comes-to-gorillas-google-photos-remains-blind/)). The model had passed its internal evaluation benchmarks. The deployment had no mechanism to detect what the model was doing to actual users in the wild. Monitoring, if it existed at all, measured throughput and latency — not the distribution of what was being predicted, nor any signal that could have caught a category of racially offensive outputs before they reached production. The failure was not a training failure. It was a deployment and monitoring failure.

---
