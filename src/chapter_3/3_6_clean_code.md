## 3.6 Clean Code

Diagrams communicate design at the level of components and relationships. Clean code applies the same design thinking at the level of individual lines, functions, and modules. The goal is identical: reduce the cognitive load imposed on the next reader. Martin's definition ([2008](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)) is not about style rules; it is about how much effort it takes to understand what the code does and why.

### 3.6.1 Naming

Names should reveal intent. Avoid abbreviations, single-letter variables (except in well-established contexts like loop counters), and misleading names.

```python
# Poor naming
def proc(d: list, f: bool) -> list:
    r = []
    for i in d:
        if i["s"] == 1 or f:
            r.append(i)
    return r

# Clean naming
def get_active_tasks(tasks: list[dict], include_archived: bool = False) -> list[dict]:
    return [
        task for task in tasks
        if task["status"] == 1 or include_archived
    ]
```

### 3.6.2 Functions

Functions should do one thing and do it well. A function that can be described with "and" in its name (e.g., `validate_and_save_task`) is doing too much. Keep functions short — typically 5–20 lines. If a function is longer, it is probably doing more than one thing.

### 3.6.3 Comments

Write code that does not need comments. When a comment is necessary, explain *why*, not *what* — the code already shows what it does.

```python
# Poor comment — explains what the code does, which is obvious
# Loop through tasks and add them to the result list
result = [task for task in tasks if task.is_active()]

# Good comment — explains a non-obvious constraint
# Skip soft-deleted tasks: the UI shows these with a strikethrough
# but the API should not return them in list endpoints
result = [task for task in tasks if not task.deleted_at]
```

### 3.6.4 Code Structure and Style

Consistent structure and formatting reduce cognitive load. For Python, follow [PEP 8](https://peps.python.org/pep-0008/) — the official style guide — and use `ruff` (introduced in Chapter 1) to enforce it automatically.

Key conventions:
- 4-space indentation
- Maximum line length: 88–120 characters (team decision)
- Two blank lines between top-level definitions
- Type annotations on all function signatures (enforced by `mypy`)

---
