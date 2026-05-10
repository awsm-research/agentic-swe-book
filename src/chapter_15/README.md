# Chapter 15: Model Evaluation, Registry, and Governance

> *"A model without an evaluation methodology is not a contribution — it is a claim."*
> — David Donoho

---

In 2017, the UK's Royal Free NHS Foundation Trust began deploying an AI system called Streams — developed by DeepMind — to identify patients at risk of acute kidney injury. The system had been evaluated on historical patient records with reported AUC values that appeared highly competitive. What the evaluation had not surfaced was that the data used to train and evaluate the model had been transferred without adequate patient consent notification, and that the evaluation methodology had not been independently validated against the patient populations the system would serve in practice. These concerns were not discovered until a 2019 review by the UK Information Commissioner's Office, roughly two years after the system had entered clinical use, which found that the Royal Free had not complied with data protection law. The NHS did not renew the DeepMind contract in 2020. The model had passed every internal quality check it had been given. The checks were simply the wrong ones.

---
