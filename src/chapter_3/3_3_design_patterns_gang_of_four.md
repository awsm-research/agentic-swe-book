## 3.3 Design Patterns (Gang of Four)

Principles tell you what to aim for; patterns show you how to get there. In 1994, Gamma, Helm, Johnson, and Vlissides catalogued 23 recurring design problems and their solutions in *Design Patterns: Elements of Reusable Object-Oriented Software* ([Gamma et al., 1994](https://en.wikipedia.org/wiki/Design_Patterns)) — a catalog that has remained in print and in use for thirty years. The "Gang of Four" (GoF) organised the patterns into three categories:

- **Creational**: How objects are created
- **Structural**: How objects are composed
- **Behavioural**: How objects interact and distribute responsibility

Notice how each pattern in this section is a direct encoding of the principles above. The Factory Method enforces OCP by letting you add new types without modifying existing creation logic. Strategy encodes OCP and DIP by depending on an abstraction rather than a concrete algorithm. Repository applies DIP to persistence. Keeping this connection visible is the point: patterns are not recipes to memorise — they are names for principled solutions.

We cover the patterns most commonly encountered in Python backend development.

### 3.3.1 Singleton (Creational)

Ensures a class has only one instance and provides a global access point to it.

**Use case**: Database connection pools, configuration objects, logging instances.

```python
# singleton.py
class DatabaseConnection:
    _instance: "DatabaseConnection | None" = None

    def __new__(cls) -> "DatabaseConnection":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connect()
        return cls._instance

    def _connect(self) -> None:
        # Initialise the connection once
        self.connection = "connected"  # placeholder

    def query(self, sql: str) -> list:
        # Execute query using self.connection
        return []


# Both variables point to the same instance
db1 = DatabaseConnection()
db2 = DatabaseConnection()
assert db1 is db2  # True
```

**Caution**: Singletons introduce global state, which can make testing difficult. In Python, dependency injection (passing the instance explicitly) is often preferable.

### 3.3.2 Factory Method (Creational)

Defines an interface for creating objects but lets subclasses decide which class to instantiate.

**Use case**: Creating notification objects (email, SMS, push) based on user preference.

```python
# factory.py
from abc import ABC, abstractmethod


class Notification(ABC):
    @abstractmethod
    def send(self, message: str, recipient: str) -> None: ...


class EmailNotification(Notification):
    def send(self, message: str, recipient: str) -> None:
        print(f"Sending email to {recipient}: {message}")


class SMSNotification(Notification):
    def send(self, message: str, recipient: str) -> None:
        print(f"Sending SMS to {recipient}: {message}")


def create_notification(channel: str) -> Notification:
    """Factory function — returns the appropriate Notification subclass."""
    channels: dict[str, type[Notification]] = {
        "email": EmailNotification,
        "sms": SMSNotification,
    }
    if channel not in channels:
        raise ValueError(f"Unknown notification channel: {channel}")
    return channels[channel]()


# Usage
notifier = create_notification("email")
notifier.send("Your task has been assigned.", "alice@example.com")
```

### 3.3.3 Observer (Behavioural)

Defines a one-to-many dependency between objects so that when one object changes state, all its dependents are notified automatically.

**Use case**: Event systems, UI data binding, notification pipelines.

```python
# observer.py
from abc import ABC, abstractmethod


class EventListener(ABC):
    @abstractmethod
    def on_event(self, event: dict) -> None: ...


class TaskEventBus:
    def __init__(self) -> None:
        self._listeners: list[EventListener] = []

    def subscribe(self, listener: EventListener) -> None:
        self._listeners.append(listener)

    def publish(self, event: dict) -> None:
        for listener in self._listeners:
            listener.on_event(event)


class EmailNotifier(EventListener):
    def on_event(self, event: dict) -> None:
        if event.get("type") == "task_assigned":
            print(f"Email: task {event['task_id']} assigned to {event['assignee']}")


class AuditLogger(EventListener):
    def on_event(self, event: dict) -> None:
        print(f"Audit log: {event}")


# Usage
bus = TaskEventBus()
bus.subscribe(EmailNotifier())
bus.subscribe(AuditLogger())

bus.publish({"type": "task_assigned", "task_id": "123", "assignee": "alice"})
```

### 3.3.4 Strategy (Behavioural)

Defines a family of algorithms, encapsulates each one, and makes them interchangeable.

**Use case**: Sorting algorithms, payment processing, priority calculation.

```python
# strategy.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass
class Task:
    id: str
    title: str
    due_date: date
    priority: int  # 1 (low) to 4 (critical)


class SortStrategy(ABC):
    @abstractmethod
    def sort(self, tasks: list[Task]) -> list[Task]: ...


class SortByDueDate(SortStrategy):
    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(tasks, key=lambda t: t.due_date)


class SortByPriority(SortStrategy):
    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(tasks, key=lambda t: t.priority, reverse=True)


class TaskList:
    def __init__(self, strategy: SortStrategy) -> None:
        self._strategy = strategy

    def set_strategy(self, strategy: SortStrategy) -> None:
        self._strategy = strategy

    def get_sorted(self, tasks: list[Task]) -> list[Task]:
        return self._strategy.sort(tasks)
```

### 3.3.5 Repository (Architectural Pattern)

While not in the original GoF catalog, the Repository pattern ([Fowler, 2002](https://martinfowler.com/eaaCatalog/repository.html)) is essential in modern backend development. It abstracts the data access layer, presenting a collection-like interface to the domain model.

```python
# repository.py
from abc import ABC, abstractmethod
from uuid import UUID
from dataclasses import dataclass
from datetime import date


@dataclass
class Task:
    id: UUID
    title: str
    due_date: date | None = None


class TaskRepository(ABC):
    """Abstract repository — defines the interface."""

    @abstractmethod
    def find_by_id(self, task_id: UUID) -> Task | None: ...

    @abstractmethod
    def find_all_by_project(self, project_id: UUID) -> list[Task]: ...

    @abstractmethod
    def save(self, task: Task) -> Task: ...

    @abstractmethod
    def delete(self, task_id: UUID) -> None: ...


class InMemoryTaskRepository(TaskRepository):
    """In-memory implementation — used in tests."""

    def __init__(self) -> None:
        self._store: dict[UUID, Task] = {}

    def find_by_id(self, task_id: UUID) -> Task | None:
        return self._store.get(task_id)

    def find_all_by_project(self, project_id: UUID) -> list[Task]:
        return list(self._store.values())  # simplified

    def save(self, task: Task) -> Task:
        self._store[task.id] = task
        return task

    def delete(self, task_id: UUID) -> None:
        self._store.pop(task_id, None)
```

The key benefit: services depend on the abstract `TaskRepository`, not on a specific database implementation. Swapping PostgreSQL for SQLite in tests requires only a different concrete class.

---
