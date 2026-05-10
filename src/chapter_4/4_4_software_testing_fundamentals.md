## 4.4 Software Testing Fundamentals

Software testing is the process of evaluating and verifying that a software system meets its requirements and behaves as expected. It is an empirical activity: tests cannot prove the absence of bugs, only their presence.

### 4.4.1 Why Testing Matters

Testing serves several purposes:

- **Defect detection**: finding bugs before they reach users
- **Regression prevention**: ensuring that new changes do not break existing functionality
- **Design feedback**: tests that are hard to write often indicate design problems
- **Documentation**: a well-named test suite describes exactly what a system does
- **Confidence**: a passing test suite gives the team confidence to make changes

Every team must test. The real decision is which tests to write, at what level, and in what quantity — given the risk profile and time available.

### 4.4.2 Fault, Error, and Failure

These three terms are often used interchangeably in informal conversation but have precise technical meanings:

- **Fault** (defect): a static flaw in the code or design — for example, an off-by-one error in a loop condition. A fault is latent until it is exercised.
- **Error**: an incorrect internal state that results from executing a fault — for example, a variable holding the wrong value.
- **Failure**: the externally observable manifestation of an error — for example, a crash, an incorrect output, or a security breach.

```
Fault (code defect)
    ↓  when executed
Error (incorrect state)
    ↓  when propagated to output
Failure (visible incorrect behaviour)
```

The goal of testing is to trigger failures so that faults can be identified and removed before the software is deployed. A fault that is never exercised by any test may remain dormant until it is triggered in production.

### 4.4.3 Verification and Validation

Two complementary questions must be answered for any software system:

- **Verification** — *"Are we building the product right?"* Does the software conform to its specification? Verification activities include code review, static analysis, and unit testing against a formal specification.
- **Validation** — *"Are we building the right product?"* Does the software meet the actual needs of users? Validation activities include acceptance testing, user research, and beta testing.

A system can be thoroughly verified (it exactly matches the specification) but fail validation (the specification was wrong). Conversely, a system can satisfy users in informal testing but contain specification violations that create security or reliability risks.

---

### 4.4.4 The Testing Pyramid

The *testing pyramid* ([Cohn, 2009](https://www.mountaingoatsoftware.com/books/succeeding-with-agile-software-development-using-scrum)) describes the ideal distribution of test types:

```
          ┌───────────┐
          │   E2E /   │   Few, slow, fragile — test critical paths only
          │ UI Tests  │
         ┌┴───────────┴┐
         │ Integration  │  Some — test component interactions
         │    Tests     │
        ┌┴──────────────┴┐
        │   Unit Tests    │  Many — fast, isolated, precise
        └────────────────┘
```

**Unit tests** are the foundation: fast, isolated, numerous. They test individual functions or classes in isolation.

**Integration tests** verify that components work correctly together — services calling repositories, API handlers interacting with business logic.

**End-to-end (E2E) tests** exercise the system as a whole, simulating real user interactions. They are slow, brittle, and expensive to maintain — use them sparingly, for critical user journeys only.

This distribution is sometimes called the "1:10:100 rule" — for every E2E test, write ~10 integration tests and ~100 unit tests. The exact ratio varies by system, but the principle holds: favour fast, isolated tests over slow, coupled ones.

### 4.4.5 Black-Box Testing

In black-box testing, the tester has no knowledge of the internal implementation. Tests are derived entirely from the specification — inputs are provided and outputs are verified against expected behaviour.

**Advantages**: Tests are specification-driven; a new implementation can be tested without modifying the tests; tests reflect user-visible behaviour.

**Techniques:**
- **Equivalence partitioning**: Divide inputs into classes that the system should handle identically. Test one representative from each class.
- **Boundary value analysis**: Test at the boundaries of valid input ranges. Bugs cluster at boundaries (off-by-one errors, empty inputs, maximum values).
- **Decision table testing**: For systems with complex conditional logic, enumerate all combinations of conditions and expected outcomes.

**Example — equivalence partitioning for `divide(a, b)`:**

The `b` parameter has two meaningful partitions:
- **Valid (non-zero)**: any `b != 0`, e.g. `2`, `-3`, `0.5`
- **Invalid (zero)**: `b == 0`, which should raise `ValueError`

Test one value from each partition: `divide(10, 2)` (valid path), `divide(10, 0)` (zero guard).

### 4.4.6 White-Box Testing

In white-box testing (also called structural or glass-box testing), the tester has full knowledge of the internal implementation. Tests are derived from the source code, with the goal of exercising specific paths, branches, and conditions.

**Techniques:**
- **Statement coverage**: Every statement is executed by at least one test
- **Branch coverage**: Every branch (if/else, loop) is executed in both directions
- **Path coverage**: Every possible path through the code is executed (often infeasible for complex code)

White-box testing is particularly valuable for finding dead code, unreachable branches, and logic errors that black-box tests might miss.

---
