## 4.5 Levels of Testing

Testing is typically organised into four levels, each with a different scope, objective, and owner.

### 4.5.1 Acceptance Testing

**Scope**: the system from the user's perspective.

**Objective**: validate (not just verify) that the system meets real user needs. Acceptance tests are defined in terms of user stories or business scenarios, not technical specifications.

**Characteristics**: written collaboratively by developers, testers, and product owners; often expressed in plain language using frameworks like Cucumber or Robot Framework. The final gate before a release.

**Example**: "Given a user with an existing account, when they create a task with a future due date, then the task appears in their dashboard sorted by due date."

### 4.5.2 System Testing

**Scope**: the entire system as a deployed whole.

**Objective**: verify that the system meets its functional and non-functional requirements in an environment that resembles production — including load balancers, external services, and realistic data volumes.

**Characteristics**: slow, expensive, typically run in a dedicated staging environment before a release. Covers performance, security, and reliability alongside functional correctness.

**Example**: a load test that sends 1,000 concurrent task-creation requests and verifies that all succeed within 500 ms at the 95th percentile.

### 4.5.3 Integration Testing

**Scope**: interactions between two or more components — for example, a service and its repository, or an API handler and its business logic layer.

**Objective**: verify that components communicate correctly and that integration assumptions (data formats, error handling, transaction boundaries) hold.

**Characteristics**: slower than unit tests (seconds per test), may require a running database or message broker, written by developers.

**Example**: testing that saving a task via the repository and then retrieving it by ID returns the same data, end to end through the real database driver.

### 4.5.4 Unit Testing

**Scope**: a single function, method, or class in isolation.

**Objective**: verify that each unit of code behaves correctly according to its contract. External dependencies (databases, APIs, file systems) are replaced with mocks or stubs.

**Characteristics**: fast (milliseconds per test), deterministic, run on every commit, written by developers.

**Example**: testing that `add(3, 5)` returns `8.0`, and that `divide(10, 0)` raises `ValueError`.

> **Key idea**: No single level catches everything. Acceptance tests miss deeply nested logic errors that no user scenario reaches; unit tests miss failures that only appear when two components interact. The four levels are not redundant — they are complementary, each surfacing what the others cannot.

Unit tests sit at the base of the pyramid because they are fast enough to run on every commit and precise enough to pinpoint exactly which function broke. The next section shows how to write them in Python.

---
