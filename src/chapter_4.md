# Chapter 4: Software Quality & Testing

> *"Testing shows the presence, not the absence of bugs."*
> — Edsger W. Dijkstra

---

## Learning Objectives

By the end of this chapter, you will be able to:

1. Define software quality and explain its key attributes according to ISO 25010.
2. Distinguish between functional quality, structural quality, and process quality.
3. Explain the difference between verification and validation, and between fault, error, and failure.
4. Describe the levels of testing and when to apply each.
5. Write unit tests in Python using unittest, and run tests and measure coverage with pytest.
6. Measure and interpret code coverage and understand its limitations.
7. Critically evaluate AI-generated tests and understand why AI cannot replace a thoughtful testing strategy.

---

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

## 4.2 Software Quality Assurance (SQA)

Software Quality Assurance (SQA) is the set of systematic processes and activities that ensure software products and processes conform to defined standards and meet quality objectives.

### Goals of SQA

- **Product quality**: ensuring the delivered software is correct, reliable, and secure
- **Process quality**: ensuring the development process is disciplined, repeatable, and measurable
- **Continuous quality control**: detecting and preventing defects throughout the lifecycle, not just at the end

SQA encompasses reviews, audits, testing, static analysis, and process monitoring. Standards such as ISO/IEC 25010 and ISO 9001 provide frameworks for defining and measuring quality systematically.

### Stakeholders

Quality is a shared concern across multiple groups:

| Stakeholder | Quality concern |
|-------------|----------------|
| **Users** | Does the software do what I need, reliably and safely? |
| **Developers** | Is the code correct, maintainable, and testable? |
| **Sponsors / management** | Does the product meet requirements on time and within budget? |

When these concerns conflict — for example, when sponsors want to cut testing to meet a deadline — SQA provides the data (defect rates, coverage metrics, risk assessments) to make that trade-off visible before it is made, not after it backfires.

---

## 4.3 Software Quality Dimensions

Software quality can be decomposed along three complementary dimensions.

### Functional Quality

Functional quality measures whether the software correctly implements its intended behaviour. It is evaluated by testing: does the software produce the right outputs for all valid inputs, and behave correctly at boundaries and in error conditions?

### Structural Quality (Non-Functional)

Structural quality measures properties of the system that are not directly visible in outputs but affect long-term viability:

- **Usability**: can users accomplish tasks efficiently with low error rates?
- **Security**: does the system resist known attack vectors?
- **Performance**: does the system meet latency and throughput requirements under load?
- **Maintainability**: can developers understand, modify, and extend the codebase?

### Process Quality

Process quality measures how software is built: are requirements gathered rigorously? Are code reviews conducted? Is CI/CD enforced? A poor process consistently produces poor products, even when individual engineers are skilled.

### ISO 25010 Quality Model

The ISO/IEC 25010 standard ([ISO, 2011 edition](https://www.iso.org/standard/35733.html); revised 2023) defines eight top-level quality characteristics:

| Characteristic | Description |
|---------------|-------------|
| **Functional suitability** | Degree to which functions meet stated and implied needs |
| **Reliability** | Ability to perform specified functions under defined conditions |
| **Performance efficiency** | Performance relative to resources used |
| **Usability** | Effectiveness, efficiency, and satisfaction of use |
| **Security** | Protection of information and data |
| **Maintainability** | Effectiveness with which the product can be modified |
| **Compatibility** | Ability to exchange and use information with other systems |
| **Portability** | Ability to be transferred to different environments |

Each characteristic is further decomposed into sub-characteristics. For example, *reliability* includes fault tolerance, recoverability, and availability.

---

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

## 4.6 Unit Testing in Python

### 4.6.1 The Anatomy of a Unit Test

Every unit test answers three questions:

- **Expected input** — what data is the unit given?
- **Expected output** — what should the unit produce for that input?
- **Actual output** — what did the unit actually produce?

When expected and actual outputs match, the test passes. When they diverge, the test fails and the discrepancy pinpoints what the code got wrong. This simple structure is formalised as the **Arrange–Act–Assert (AAA)** pattern.

Recall the full calculator from Tutorial 1 (extended in the Step 8 activity):

```python
# src/calculator.py
def add(a: float, b: float) -> float:
    return a + b

def subtract(a: float, b: float) -> float:
    return a - b

def multiply(a: float, b: float) -> float:
    return a * b

def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

A unit test for `add` looks like this:

```python
import unittest
from src.calculator import add

class TestAdd(unittest.TestCase):
    def test_add_returns_correct_sum(self):
        # Arrange — set up inputs
        a = 3
        b = 5

        # Act — call the unit under test
        result = add(a, b)

        # Assert — compare actual output to expected output
        self.assertEqual(result, 8)
```

Keeping the three phases visually separate — even with a blank line — makes the test's intent immediately clear to the next reader. When a test fails, the `Act` line is the fault site and the `Assert` line tells you what was wrong.

> **Activity:** Following the same AAA pattern, write one test for each of the remaining operations:
> - `test_subtract_returns_correct_difference` — e.g. `subtract(10, 3)` should return `7`
> - `test_multiply_returns_correct_product` — e.g. `multiply(4, 5)` should return `20`
> - `test_divide_returns_correct_quotient` — e.g. `divide(10, 2)` should return `5.0`

### 4.6.2 Assertion Methods in unittest

`unittest.TestCase` provides named assertion methods on `self`. Each method produces a descriptive failure message automatically — you do not need to write one.

**Equality and comparison:**

```python
self.assertEqual(add(3, 5), 8)          # fails if not equal
self.assertNotEqual(add(3, 5), 0)       # fails if equal
self.assertAlmostEqual(add(0.1, 0.2), 0.3, places=10)  # safe for floats
self.assertTrue(add(1, 1) > 0)          # fails if expression is False
```

**Checking exceptions with `assertRaises`:**

When a unit should raise an exception for invalid input, use `assertRaises` as a context manager. The test fails if the exception is *not* raised.

```python
from src.calculator import divide

class TestDivide(unittest.TestCase):
    def test_divide_raises_on_zero(self):
        # Arrange
        a = 10
        b = 0

        # Act + Assert — the exception is the expected output
        with self.assertRaises(ValueError):
            divide(a, b)
```

To also check the exception message, use `assertRaisesRegex`:

```python
    def test_divide_raises_correct_message(self):
        with self.assertRaisesRegex(ValueError, "Cannot divide by zero"):
            divide(10, 0)
```

**Common assertion methods:**

| Scenario | Method |
|----------|--------|
| Values are equal | `self.assertEqual(a, b)` |
| Values are not equal | `self.assertNotEqual(a, b)` |
| Floats are approximately equal | `self.assertAlmostEqual(a, b, places=N)` |
| Condition is true | `self.assertTrue(expr)` |
| Function raises exception | `with self.assertRaises(SomeError):` |
| Exception message matches | `with self.assertRaisesRegex(SomeError, "pattern"):` |

### 4.6.3 Code Coverage

Writing tests is not enough — you also need to know which parts of the code are actually being executed by those tests. **Code coverage** measures this.

**Running coverage with pytest-cov:**

```bash
uv add --dev pytest-cov
pytest --cov=src --cov-report=term-missing
```

If your tests only cover `add` and not `divide`, the report will flag the untested lines:

```
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
src/calculator.py             9      3    67%   8-10
-------------------------------------------------------
TOTAL                         9      3    67%
```

The `Missing` column shows the exact lines not reached by any test — these are your blind spots. Lines 8–10 correspond to the `if b == 0` guard and the return inside `divide`.

**Statement coverage vs. branch coverage:**

Statement coverage (the default) counts whether each *line* was executed. Branch coverage goes further: it checks whether each *decision* was exercised in both directions.

The `divide` function has two branches: the normal path and the zero-division guard. A single test with `b != 0` executes the return statement but never enters the `if` block. To reach 100% branch coverage, you need one test per branch:

```python
def test_divide_normal(self):
    self.assertEqual(divide(10, 2), 5.0)   # exercises the normal branch

def test_divide_by_zero(self):
    with self.assertRaises(ValueError):
        divide(10, 0)                       # exercises the guard branch
```

Run branch coverage with:

```bash
pytest --cov=src --cov-branch --cov-report=term-missing
```

**Limitations of coverage:**

Coverage tells you which code was *executed*, not whether it was *tested correctly*. Consider:

```python
class TestCoverageTrap(unittest.TestCase):
    def test_coverage_trap(self):
        add(3, 5)   # no assertion
```

This test executes `add` — contributing to coverage — but asserts nothing. A bug that made `add` return `0` for all inputs would go undetected. High coverage with weak assertions is worse than honest low coverage, because it creates false confidence.

Two rules of thumb:
- Aim for ≥80% statement coverage on business logic; 100% branch coverage on code with error-handling paths.
- Coverage is a floor, not a ceiling. A 95% covered codebase with no assertions on the remaining 5% may still ship critical bugs in those five lines.

---
