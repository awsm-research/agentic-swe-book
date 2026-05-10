## 3.2 Design Principles

Before reaching for a named pattern or an architectural blueprint, a developer needs values — a set of guidelines that make it possible to reason about whether a design is getting better or worse. Design principles play that role. They do not tell you *what* to build; they tell you *how to judge* what you build.

### 3.2.1 SOLID Principles

The SOLID principles ([Martin, 2000](https://web.archive.org/web/20150906155800/http://www.objectmentor.com/resources/articles/Principles_and_Patterns.pdf)) are five guidelines for writing maintainable object-oriented code:

**S — Single Responsibility Principle (SRP)**

> A class should have only one reason to change.

A class that handles HTTP parsing, business logic, *and* database queries will need to change whenever any of those three concerns changes. Separating them into different classes means each has one reason to change.

```python
# Violates SRP — this class does too much
class TaskService:
    def create_task(self, title: str, user_id: str) -> dict:
        # Business logic
        if not title.strip():
            raise ValueError("Title cannot be empty")
        # Database access (should be in repository)
        db.execute("INSERT INTO tasks ...")
        # Email sending (should be in notification service)
        smtp.send_email(user_id, "Task created")
        return {"id": "...", "title": title}
```

**O — Open/Closed Principle (OCP)**

> Software entities should be open for extension, but closed for modification.

You should be able to add new behaviour without modifying existing code. The Strategy pattern in Section 3.3.4 is a direct application of OCP: new sort strategies can be added without modifying `TaskList`.

**L — Liskov Substitution Principle (LSP)**

> Objects of a subclass should be substitutable for objects of the superclass without altering program correctness.

If `InMemoryTaskRepository` is a subclass of `TaskRepository`, any code that works with `TaskRepository` must work identically with `InMemoryTaskRepository`. Violating LSP typically indicates that the inheritance relationship is wrong.

**I — Interface Segregation Principle (ISP)**

> Clients should not be forced to depend on interfaces they do not use.

Rather than one large interface, prefer several small, focused ones. A `ReadOnlyTaskRepository` interface (with only `find_by_id` and `find_all`) is more appropriate for a reporting service than a full `TaskRepository` that includes `save` and `delete`.

**D — Dependency Inversion Principle (DIP)**

> High-level modules should not depend on low-level modules. Both should depend on abstractions.

```python
# Violates DIP — TaskService depends directly on the concrete PostgreSQL implementation
class TaskService:
    def __init__(self) -> None:
        self.repo = PostgresTaskRepository()  # concrete dependency

# Follows DIP — TaskService depends on the abstract interface
class TaskService:
    def __init__(self, repo: TaskRepository) -> None:
        self.repo = repo  # injected abstraction
```

This is *dependency injection* — the concrete implementation is passed in from outside, typically by an application container. It makes `TaskService` testable with `InMemoryTaskRepository`.

### 3.2.2 DRY: Don't Repeat Yourself

> Every piece of knowledge must have a single, unambiguous, authoritative representation within a system. ([Hunt & Thomas, 1999](https://pragprog.com/titles/tpp/the-pragmatic-programmer/))

Duplicated code is duplicated knowledge. When the logic changes (and it will), you must find and update every copy. The solution is not always to extract a function — sometimes the duplication is accidental and the two pieces of code will diverge. Use judgment: extract when the duplication represents the *same concept*, not just the same syntax.

### 3.2.3 Composition Over Inheritance

Prefer composing objects from smaller, focused components over building deep inheritance hierarchies. Inheritance creates tight coupling between parent and child; composition allows components to be mixed and matched.

### 3.2.4 Hollywood Principle

> "Don't call us, we'll call you."

High-level components should control when and how low-level components are used, not the reverse. This is the principle behind inversion of control (IoC) frameworks and the Observer pattern.

---
