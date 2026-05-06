# Chapter 3 — Design Principles & Patterns

Code samples extracted from Chapter 3 (Section 3.2 SOLID, Section 3.3 GoF Patterns,
Section 3.6 Clean Code).

## Files

| File | Demonstrates |
|---|---|
| `srp_violation.py` | A class that violates the Single Responsibility Principle |
| `dip_example.py` | Dependency Inversion violation vs. injected abstraction |
| `singleton.py` | Singleton creational pattern |
| `factory.py` | Factory Method creational pattern with `Notification` hierarchy |
| `observer.py` | Observer behavioural pattern with `TaskEventBus` |
| `strategy.py` | Strategy behavioural pattern with sortable `TaskList` |
| `repository.py` | Repository pattern with `InMemoryTaskRepository` |
| `clean_naming.py` | Poor vs. clean naming side-by-side from Section 3.6.1 |

## How to run

These are illustrative snippets from the chapter. `srp_violation.py` and
`dip_example.py` reference symbols (`db`, `smtp`, `PostgresTaskRepository`,
`TaskRepository`) that are not defined — they are intentionally incomplete to
highlight the principle being violated. The other files are self-contained and
can be executed directly:

```bash
python factory.py
python observer.py
python singleton.py
```
