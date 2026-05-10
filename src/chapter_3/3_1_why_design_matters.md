## 3.1 Why Design Matters

Writing code that works is necessary but not sufficient. Code must also be maintainable — readable and modifiable by other developers (and by your future self) over months and years. Poor design decisions made early in a project compound over time: a monolithic module that is difficult to test becomes more difficult to test as it grows; a tangled dependency structure becomes harder to untangle as more code depends on it.

Software design is the activity of deciding *how* a system will be structured before (or alongside) the activity of writing code. Good design:

- Makes the system easier to understand
- Makes the system easier to test
- Makes the system easier to change in response to new requirements
- Reduces the risk of introducing bugs when modifying existing functionality

This chapter builds that understanding from the inside out. We begin with the principles that define *what makes a design good*, then examine the named patterns that encode those principles as reusable solutions, then the architectural strategies that compose those patterns at the scale of an entire system, and finally the notation used to communicate all of it. Each layer depends on the one before it — a pattern that cannot be explained in terms of a principle is a recipe, not a design.

---
