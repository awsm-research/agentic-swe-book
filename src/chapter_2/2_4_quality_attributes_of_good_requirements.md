## 2.4 Quality Attributes of Good Requirements

Individual requirements should satisfy the following quality criteria. The IEEE 830 standard ([IEEE, 1998](https://standards.ieee.org/ieee/830/1222/)) and its successor ISO/IEC/IEEE 29148 ([2018](https://www.iso.org/standard/72052.html)) are the canonical references.

| Attribute | Description | Bad Example | Good Example |
|---|---|---|---|
| **Correct** | Accurately represents stakeholder needs | — | Validated with stakeholders |
| **Unambiguous** | Has only one possible interpretation | "The system shall be user-friendly" | "A new user shall create their first task in under 3 minutes" |
| **Complete** | Covers all necessary conditions | "Users can log in" | "Users can log in with email/password; failed attempts are logged; accounts lock after 5 failures" |
| **Consistent** | Does not conflict with other requirements | Two requirements with contradictory session expiry rules | All session management requirements align |
| **Verifiable** | Can be tested or inspected | "The system shall be reliable" | "The system shall achieve 99.9% uptime" |
| **Traceable** | Can be linked to its source | Requirement with no stakeholder owner | Requirement tagged to specific stakeholder interview |
| **Prioritised** | Ranked by importance | No priority information | MoSCoW category assigned |

---
