## 17.8 MedChat: Architectural Constraints in Practice

---

MedChat is the clinical Q&A chatbot that serves as the case study for Chapters 17–21. It is designed for use by qualified healthcare professionals — physicians, nurses, and pharmacists — who need rapid access to clinical guidelines, drug interaction information, and evidence-based practice protocols. The architectural decisions in MedChat are not arbitrary engineering preferences; they follow directly from the constraints discussed in this chapter.

### 17.8.1 Why RAG Is Non-Negotiable for MedChat

A clinical chatbot that relies on a foundation model's parametric knowledge for drug information and clinical guidelines cannot be deployed safely. The model's knowledge has a training cutoff. Drug approvals, guideline updates, and formulary changes occur continuously. A model trained in 2023 does not know about a guideline revision published in 2024. More critically, a model trained on publicly available data does not know about a specific hospital's local formulary, antimicrobial stewardship protocols, or patient-population-specific adaptations.

The retrieval layer is therefore a safety requirement, not a quality preference. MedChat's document corpus — comprising WHO clinical guidelines, drug interaction reference tables, and clinical FAQ documents — is the system's source of truth. The model's role is to synthesise and communicate information from that corpus, not to recall facts from its weights. Every factual claim in a MedChat response must be attributable to a specific retrieved passage. When it is not, the system must flag that explicitly.

### 17.8.2 Context Window Allocation for MedChat

The MedChat context window allocation reflects the priority ordering that clinical safety demands. The system prompt receives a generous allocation — approximately 500 tokens — because it carries the instructions that define scope, safety constraints, and citation requirements. These instructions must not be crowded out by other content. Retrieved context receives two to three thousand tokens: enough for four to six relevant passages that can together address the clinical question from multiple angles. Conversation history is limited actively: after five turns, older history is summarised rather than accumulated, preventing context drift while preserving coherent multi-turn dialogue. The current query and response reserve are kept moderate, because clinical answers should be thorough but not verbose.

This allocation is not the only valid one, but it reflects a deliberate tradeoff: quality and safety take precedence over history breadth and cost minimisation. A different application — a general consumer health information service — might allocate differently. The point is that the allocation must be deliberate, not accidental.

### 17.8.3 Failure Mode Priorities for MedChat

The relative danger of each failure mode differs across applications. For MedChat, the priority ordering is clear. Hallucination on clinical facts is the most dangerous failure: an incorrect drug dosage or a fabricated contraindication could contribute to patient harm. The RAG architecture and faithfulness guardrails address this directly. Sycophancy is the second priority: a clinician who states an incorrect assumption about a medication must be corrected, not validated. The system prompt must explicitly instruct the model to prioritise accuracy over agreement. Refusal of legitimate clinical queries is a usability concern, not a safety concern: a refused query is frustrating but not dangerous. Context drift over long sessions is the lowest priority because clinical sessions tend to be shorter and more focused than general conversational sessions.

This priority ordering shapes not just the architecture but the evaluation strategy: evaluation resources are concentrated where the risk is highest. A test suite that thoroughly evaluates hallucination and sycophancy but only lightly covers refusal and context drift reflects an appropriate allocation of engineering effort for this domain.

---
