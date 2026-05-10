## 4.1 Introduction to Software Quality

Software quality is the degree to which a software system meets its specified requirements and satisfies user needs. It is not a binary property — software is not simply "good" or "bad" — but a multi-dimensional profile of attributes that must be traded off against each other and against cost and time.

Key quality attributes include:

- **Reliability**: the software produces correct results under normal and adverse conditions
- **Correctness**: the software conforms to its specification
- **Security**: the software is resistant to unauthorised access and misuse
- **Usability**: the software is intuitive and efficient for its intended users
- **Maintainability**: the software can be modified, extended, and debugged with reasonable effort

**Quality is everyone's responsibility.** A common misconception is that quality belongs to a dedicated QA team. Quality is shaped by every decision made during design, development, and deployment — by the developer who skips input validation, the designer who ignores edge cases, and the project manager who cuts the testing phase. There is no dedicated "quality phase"; there are only decisions that raise or lower it.

> **Key Insight**: Software defects cost the global economy an estimated $2.08 trillion annually ([CISQ, 2020](https://www.it-cisq.org/the-cost-of-poor-quality-software-in-the-us-a-2020-report/)). The cost to fix a defect grows by an order of magnitude at each phase of development — a bug caught in code review costs roughly 10× less to fix than one caught in production. Quality investment at the start is not an overhead; it is the cheapest form of defect prevention.

---
