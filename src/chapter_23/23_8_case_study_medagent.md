## 23.8 Case Study: MedAgent

---

MedAgent is a constructed example developed for this book to illustrate how the patterns in this chapter combine in a production-realistic context. It serves as the running example throughout this book.

### System Architecture

MedAgent uses a supervisor/worker pattern. A Coordinator Agent receives a clinician's request — "Generate a discharge summary for patient 4471" — and decomposes it into three parallel subtasks, each delegated to a specialist worker:

- The **Records Agent** retrieves the patient's structured clinical record: demographics, diagnoses, medications, allergy status, recent test results, and prior admission history.
- The **Research Agent** queries a medical knowledge base and relevant clinical guidelines to identify current best-practice recommendations applicable to this patient's condition.
- The **Drafting Agent** receives the outputs of the Records Agent and Research Agent and generates a structured discharge summary.

The Records Agent and Research Agent are dispatched in parallel — a fan-out. Their results are collected by the Coordinator — the fan-in — and passed to the Drafting Agent. The Drafting Agent is not dispatched until both upstream agents have returned results, because the draft's correctness depends on both. This dependency is a deliberate exception to pure parallelism: parallelism is maintained where the subtasks are independent, and sequenced where they are not.

### Failure Containment

Each agent operates under a timeout budget: eight seconds for the Records Agent, twelve seconds for the Research Agent, ten seconds for the Drafting Agent, within an overall workflow budget of forty-five seconds. Circuit breakers monitor each agent independently.

If the Records Agent times out, the system does not proceed to drafting. A patient record that cannot be retrieved is a required input; proceeding without it risks a summary that misrepresents the patient's actual clinical state. The workflow escalates to a human reviewer with a clear notification: "Records retrieval failed. Clinical documentation requires manual initiation."

If the Research Agent times out, the system proceeds with a reduced scope: the Drafting Agent is instructed to generate a summary based on the clinical record alone, without guideline references, and the output is marked as "Guideline lookup unavailable — clinician review required." Research retrieval is an optional enhancement; missing it degrades output quality but does not risk patient safety in the way that a missing clinical record would.

Write permissions are strictly scoped. The Records Agent has read access to the patient record and no write access. The Research Agent has no access to the patient record. The Drafting Agent has write access only to the draft document store, not to any clinical record. Only after human approval is the draft promoted to the clinical record — an operation performed by a separate service with its own audit log.

### Human-in-the-Loop Gate

MedAgent implements a single human-in-the-loop checkpoint: before the drafted note becomes a clinical record. The clinician reviews the generated summary, sees a clear provenance trail — which records were retrieved, which guidelines were referenced, which agent produced which section — and approves, edits, or rejects the draft.

The choice of a single final gate rather than multiple intermediate checkpoints is deliberate. MedAgent is designed for experienced clinicians who are capable of evaluating a completed draft and who are familiar with the patient's history. The provenance trail gives reviewers the information they need to spot errors without requiring them to approve each pipeline stage separately. The tradeoff is accepted: a clinician who does not read the draft carefully before approving it could commit an error. The system's design makes careless approval harder by requiring explicit confirmation of the provenance trail, but it cannot eliminate the human factor.

MedAgent illustrates the central discipline of multi-agent system design: not maximising what agents can do, but carefully delimiting what each agent may do, what it may access, how long it may run, and what human authority it may not substitute for.

---
