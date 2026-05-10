## 15.10 Governance in Regulated Domains

---

*Governance* in the context of ML model deployment refers to the formal processes by which an organisation decides that a model is safe and appropriate to deploy, and documents that decision in a way that satisfies regulatory requirements. It is the human-in-the-loop checkpoint that sits between model evaluation and production deployment.

Governance answers questions that engineering metrics cannot. An evaluation gate answers: does the model meet the defined quality thresholds? Governance answers: should we deploy this model, in this clinical context, for these patients, at this time? The former is a technical question. The latter requires judgement about clinical context, regulatory compliance, patient safety, and organisational risk tolerance.

In clinical AI, governance typically involves three distinct approval roles:

**Clinical lead sign-off** is the domain expert's declaration that the model's evaluation results, limitations, and intended use are consistent with safe clinical practice. The clinical lead reviews the model card, examines representative Grad-CAM outputs for clinical plausibility, and confirms that the defined deployment constraints — specific patient populations, clinician review requirements, out-of-scope uses — are appropriate. This sign-off is not a rubber stamp; it is the clinical expert's professional accountability for the deployment decision.

**Data governance review** is the organisation's confirmation that the model's training data was collected and processed in accordance with applicable data protection law and patient consent frameworks. In Australia, this involves compliance with the Privacy Act 1988 and, in healthcare settings, the My Health Records Act 2012. In the European Union, GDPR and the AI Act apply. The data governance review verifies that the consent frameworks under which patient data was collected are consistent with the use of that data to train a clinical AI system.

**Technology governance review** is the engineering team's certification that the system has been built in accordance with organisational security, reliability, and maintainability standards — that the serving infrastructure is appropriately secured, that monitoring is configured and alerting is active, and that a rollback procedure exists and has been tested.

Governance in regulated domains has auditability requirements that go beyond documentation. The Australian Therapeutic Goods Administration (TGA), which regulates clinical AI systems classified as software as a medical device, requires that organisations demonstrate the basis on which deployment decisions were made — not merely that a decision was made. The difference is significant: a record that shows "clinical lead approved version 8 on 15 March 2025" is not sufficient. The record must also show what evidence was reviewed, what criteria were applied, and what limitations were acknowledged at the time of approval. The model card, the evaluation gate results, and the registry transition metadata together constitute this evidence base.

The consequence of treating governance as bureaucracy rather than engineering is that it becomes retroactive — organisations document decisions after they have been made, to satisfy an audit, rather than before, to constrain the decision. Retroactive documentation is ineffective precisely when it matters most: when a deployed model causes harm and the question is not "was this documented" but "was this foreseeable, and what was done about it."

---
