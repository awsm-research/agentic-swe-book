# Chapter 24: Agent Safety, Observability, and Governance

> *"An agent that can act without accountability is not a tool — it is a liability. The engineering controls that make agents safe are not optional extras. They are the product."*
> — Kla Tantithamthavorn

---

In February 2024, Air Canada lost a small claims tribunal case in British Columbia after its customer-facing chatbot provided a passenger, Jake Moffatt, with incorrect information about the airline's bereavement fare policy. The chatbot told Moffatt he could apply for a bereavement discount retroactively after purchasing a full-price ticket — which was false. When Moffatt applied, Air Canada denied the refund and argued that the chatbot was a separate legal entity and the airline bore no responsibility for its output. The tribunal rejected this argument and ordered Air Canada to pay. The ruling established a principle that regulators and courts in multiple jurisdictions have since reinforced: an organisation that deploys an AI system to interact with the public on its behalf is liable for what that system does, regardless of whether the system is technically autonomous. The chatbot in the Air Canada case did not take an irreversible physical action — it produced text. An agentic system that schedules appointments, submits orders, sends communications, or modifies records on a patient's behalf is operating in categorically more dangerous territory, with correspondingly higher engineering obligations.

---
