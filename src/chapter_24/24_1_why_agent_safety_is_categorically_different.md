## 24.1 Why Agent Safety Is Categorically Different

---

When a large language model produces a harmful or incorrect response, the immediate consequence is a bad string of text. The user reads it, and that is the end of the causal chain unless a human acts further. The LLM's output is advisory. The damage it can do without human mediation is bounded by the damage that text alone can cause.

An agent does not produce advisory text. It produces actions. It calls a function that submits a purchase order. It executes a database write that updates a patient's medication list. It invokes an API that sends a message to a thousand recipients. It runs a shell command that deletes a directory. These actions have consequences in the physical or digital world that are partially or fully irreversible — and they occur without any human deciding to act on the agent's suggestion. The human is out of the causal loop, or present only at the beginning when they initiate the task and at the end when they observe the result.

The difference is structural, not a matter of degree. The software engineering discipline has spent decades developing practices for systems that do what they are told. Agents do not simply do what they are told — they pursue goals by selecting actions from a set of tools, in an order determined by their own reasoning, with outcomes that compound across steps. Each step extends the causal chain. By the time an error in the agent's reasoning becomes visible as a failed outcome, that reasoning may have already executed ten irreversible tool calls.

### 24.1.1 The Compounding Error Problem

A traditional software function either succeeds or fails at the point of execution. An agent's errors compound. Consider an agent tasked with scheduling a follow-up appointment for a discharged patient. Step one: it retrieves the patient's record. Step two: it identifies the recommended follow-up interval from the discharge summary. Step three: it checks the specialist's availability. Step four: it books the appointment and sends the confirmation. If the agent misreads the patient identifier at step one — retrieving a record for a different patient — every subsequent step executes correctly against the wrong patient's data. The appointment is booked, the confirmation is sent, and the error is invisible until the wrong patient shows up for an appointment they did not need, or until the correct patient fails to appear for an appointment they were never notified about.

In a traditional software system, a type mismatch or an incorrect identifier produces an error at the point of use. In an agent, the error produces confident, syntactically correct, semantically wrong actions. The agent has no mechanism for questioning whether its initial context was correct — it reasons within the context it was given. This is the compounding error problem, and it is the reason observability for agentic systems must capture not just the final outcome but every step of the reasoning chain.

### 24.1.2 The Irreversibility Spectrum

Not all agent actions carry the same risk. Every tool an agent can invoke sits somewhere on a spectrum from fully reversible to fully irreversible. Reading a patient record is fully reversible — the read leaves no trace and can be repeated safely. Drafting a clinical note that has not yet been saved to any system is reversible — the draft exists only in memory and is discarded if the session ends without committing it. Submitting a lab order to a hospital's ordering system is irreversible within the session — the order cannot be recalled by the agent, though it may be cancelled by a human with the appropriate access. Sending a prescription to a pharmacy is irreversible and cross-boundary — once the pharmacist has dispensed the medication, the action has propagated into the physical world.

The engineering implication is direct: the level of human oversight required before an action is executed is proportional to its irreversibility. This is not a novel principle — surgical protocols require pre-operative sign-off, financial transfer systems require dual authorisation for large wire transfers, nuclear power plants have interlocks that require multiple simultaneous human actions before certain sequences can proceed. The engineering response to irreversibility is always the same: slow down, require a second opinion, and make the decision point explicit. For agentic systems, the implementation of this principle requires deliberate architectural choices, not just careful prompting.

---
