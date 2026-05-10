## 2.3 Functional and Non-Functional Requirements

All requirements can be classified as either functional or non-functional.

### 2.3.1 Functional Requirements

Functional requirements describe *what* the system must do — specific behaviours, functions, or features. They define the interactions between the system and its environment.

**Format**: Functional requirements are often written as:
> The system shall [action] [object] [condition/qualifier].

**Examples for a task management system:**

- The system shall allow authenticated users to create tasks with a title, description, due date, and priority level.
- The system shall allow project managers to assign tasks to one or more team members.
- The system shall send an email notification to an assignee within 5 minutes of being assigned a task.
- The system shall allow users to filter tasks by status (open, in progress, completed, cancelled).

### 2.3.2 Non-Functional Requirements

Non-functional requirements (NFRs) describe *how* the system must behave — quality attributes that constrain the system's operation. They are sometimes called quality attributes or system properties.

NFRs are consistently under-specified in practice and disproportionately responsible for system failures. A system that does the right thing slowly, insecurely, or unreliably has failed on its NFRs — and those failures are often invisible until they manifest as outages, breaches, or regulatory penalties.

Key categories of non-functional requirements ([ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html)):

| Category | Description | Example |
|---|---|---|
| **Performance** | Speed and throughput | The API shall respond to 95% of requests within 200ms under a load of 1,000 concurrent users. |
| **Reliability** | Uptime and fault tolerance | The system shall achieve 99.9% uptime (≤8.7 hours downtime per year). |
| **Security** | Protection from threats | All data at rest shall be encrypted using AES-256. |
| **Scalability** | Ability to handle growth | The system shall support up to 100,000 active users without architectural changes. |
| **Usability** | Ease of use | A new user shall be able to create their first task within 3 minutes of registering. |
| **Maintainability** | Ease of change | All modules shall have unit test coverage of at least 80%. |
| **Portability** | Ability to run in different environments | The system shall run on any Linux environment with Python 3.11+. |
| **Compliance** | Adherence to regulations | The system shall comply with GDPR requirements for personal data storage and processing. |

**The danger of vague NFRs**: Non-functional requirements must be *measurable* to be useful. "The system should be fast" is not a requirement — it is a wish. "The API shall respond to 95% of requests within 200ms under a load of 1,000 concurrent users" is testable.

### 2.3.3 The FURPS+ Model

The FURPS+ model ([Grady, 1992](https://dl.acm.org/doi/10.1145/155360.155361)) provides a checklist for ensuring requirements coverage:

- **F**unctionality: Features and capabilities
- **U**sability: User interface and user experience
- **R**eliability: Availability, fault tolerance, recoverability
- **P**erformance: Speed, throughput, capacity
- **S**upportability: Testability, maintainability, portability
- **+**: Constraints (design, implementation, interface, physical)

---
