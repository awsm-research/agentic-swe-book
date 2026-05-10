## 12.5 Organisational AI Governance

### 12.5.1 AI Use Policies

An AI use policy defines:
- Which AI tools are approved for use (and for what purposes)
- What data may and may not be sent to AI services
- How AI-generated code must be reviewed before production use
- How AI tool usage should be documented

**Example policy clauses:**

> "Engineers may use approved AI coding assistants (see the approved tools list) for code generation. All AI-generated code must be reviewed by a human engineer before merging to the main branch."

> "No customer PII, authentication credentials, or proprietary algorithm details may be included in prompts to external AI services."

> "Engineers must disclose AI tool usage in pull request descriptions when AI-generated code constitutes more than 20% of the change."

### 12.5.2 Risk Tiering

The EU AI Act introduced a risk-tiered framework for AI systems ([European Parliament, 2024](https://www.europarl.europa.eu/news/en/press-room/20240308IPR19015/artificial-intelligence-act-meps-adopt-landmark-law)):

| Risk Tier | Examples | Requirements |
|---|---|---|
| **Unacceptable risk** | Social scoring, real-time biometric surveillance | Prohibited |
| **High risk** | Medical devices, hiring decisions, credit scoring | Conformity assessment, transparency, human oversight |
| **Limited risk** | Chatbots, deepfakes | Transparency obligations |
| **Minimal risk** | AI coding assistants, spam filters | Voluntary codes of conduct |

For most software development use cases, AI coding assistants fall in the "minimal risk" tier. However, if you are *building* a high-risk AI system (medical diagnosis, credit scoring, automated hiring), significantly stricter requirements apply.

### 12.5.3 Documentation and Audit Trails

Responsible AI deployment requires documentation:
- **Model cards** ([Mitchell et al., 2019](https://arxiv.org/abs/1810.03993)): Structured documents describing an AI model's intended use, limitations, evaluation results, and ethical considerations
- **Datasheets for datasets** ([Gebru et al., 2018](https://arxiv.org/abs/1803.09010)): Structured documents describing a dataset's composition, collection process, and known limitations
- **System cards**: Documentation of a deployed AI system, including the models used, their risk assessments, and mitigation measures

---
