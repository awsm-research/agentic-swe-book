## 3.7 Key Takeaways

1. **Good design is not decoration — it is risk management.** The Knight Capital incident shows that dead code, manual deployments, and missing circuit-breakers are design problems with financial and organisational consequences.

2. **SOLID principles make code resilient to change.** Each principle targets a specific source of coupling: SRP isolates reasons to change; OCP protects existing code from new requirements; LSP ensures substitutability; ISP keeps interfaces focused; DIP points high-level modules at abstractions rather than implementations.

3. **Design patterns are solutions to recurring problems, not universal prescriptions.** The GoF catalog names 23 patterns; knowing *when not to apply* a pattern is as important as knowing what it does. Singleton, in particular, is widely treated as an antipattern in testable code because it introduces hidden global state.

4. **Architecture is a high-stakes, hard-to-reverse decision.** Layered, MVC, Event-Driven, Microservices, and Monolith each fit different team sizes, scaling requirements, and operational contexts. Start with a well-structured monolith and extract services only when there is clear evidence that a component needs independent scaling.

5. **UML diagrams communicate intent, not implementation.** Use case diagrams capture scope for stakeholders; class diagrams capture static structure; sequence diagrams trace runtime behaviour; component diagrams show deployment boundaries. Each answers a different question.

6. **DRY means eliminating duplicated knowledge, not duplicated syntax.** Extract code when two pieces of logic represent the same concept; leave them separate when they merely look similar but will diverge.

7. **Clean code is an act of consideration for future readers.** Names should reveal intent, functions should do one thing, and comments should explain *why* — not narrate *what* the code already shows.

---

### Review Questions

1. A development team is building a ride-sharing platform. The backend needs to support real-time driver location updates sent to thousands of passengers simultaneously, while also handling booking, payment, and trip history. Using the architectural patterns in Section 3.4, recommend a primary pattern for the notification subsystem and justify your choice. What would the component diagram look like?

2. The sequence diagram in Section 3.5.3 shows `TaskService` delegating notification creation to `NotificationFactory`. A developer proposes replacing the factory with a direct `if/elif` block inside `TaskService`: `if preference == "email": send_email(...)`. Identify which SOLID principle this violates and explain the consequence when a third notification channel (push notification) is added.

3. A teammate argues that the Singleton pattern should be used for the application's configuration object because "there should only ever be one config." Using the caution in Section 3.3.1, explain the testability problem this creates and describe a dependency-injection alternative.

4. A legacy codebase has a `UserManager` class that handles authentication, profile updates, database queries, session management, and email sending. Identify which design principle it violates, then sketch — in pseudocode or a class diagram — how you would refactor it.

5. The Knight Capital incident involved dead code that was never removed and a manual deployment with no verification step. Map each failure to at least one design principle or practice from this chapter (e.g., SRP, DRY, Repository pattern, clean code). For each, explain how applying the principle would have reduced — though not necessarily eliminated — the risk.

---
