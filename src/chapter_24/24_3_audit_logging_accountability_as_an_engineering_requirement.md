## 24.3 Audit Logging: Accountability as an Engineering Requirement

---

Application logs and audit logs serve different purposes and must be treated as different artefacts. An application log is written to help a developer understand why the system behaved in a particular way. It may be rotated when disk space is needed, overwritten when it is old, and formatted for readability rather than queryability. An audit log is written to prove, to regulators, auditors, and courts, what the system did and who authorised it. It must be append-only, tamper-evident, and retained for legally mandated periods.

The distinction is not bureaucratic. It reflects a difference in the threat model. Application logs are threatened primarily by system failures and human error — they may be lost in a crash or misconfigured. Audit logs are threatened by both accident and intention — they may be deleted or modified by actors who wish to conceal what the system did. The engineering controls for audit logs must address both threats.

### 24.3.1 Append-Only, Tamper-Evident Records

An append-only audit log is a log to which records can only be added, never modified or deleted, by the application that generates them. The standard implementation in relational databases is to grant the application's service account INSERT permissions on the audit table while explicitly revoking UPDATE and DELETE permissions. A record written to the audit table cannot be changed through the normal application database connection; changing it requires either database administrator access or a physical modification of the storage medium.

Tamper-evidence extends this further. A tamper-evident log is one in which any modification of a historical record is detectable, even by an actor with database administrator access. The classical technique is hash chaining: each audit record includes a cryptographic hash of the previous record's content. If any record is modified, the hash chain breaks, and a verification routine that traverses the chain will detect the break at the point of modification. More robust approaches involve writing hash values to an external, append-only store — a write-once object storage service, a blockchain ledger, or a notarisation service — such that even the database administrator cannot silently modify a historical record.

The legal significance of append-only, tamper-evident audit logs is substantial. In a regulatory proceeding or civil litigation, an audit log that can be demonstrated to be tamper-evident carries evidentiary weight that an ordinary application log does not. The log is evidence of what the system did, not just what the system reported doing. For a clinical AI system that has taken an action resulting in patient harm, this distinction determines whether the organisation can prove that its system behaved as claimed.

### 24.3.2 What an Audit Record Must Contain

An audit record for an agentic system action must contain, at minimum: a unique event identifier, the session identifier that links this event to the full session trace, the timestamp of the event in a verifiable timezone format, the identity of the user who initiated the session, the identity of any human approver who authorised an irreversible action, the action type and its parameters, and the outcome of the action. For clinical AI systems, it must also contain the version of the model and system prompt active at the time of the session, so that the record can be interpreted in the context of the system configuration that produced it.

These are not arbitrary fields. Each one answers a question that a regulator, auditor, or litigant will ask: What was done? When? By which version of the system? Who initiated it? Who authorised it? What was the result? A system whose audit log cannot answer these questions is not audit-ready, regardless of how sophisticated its reasoning capabilities are.

---
