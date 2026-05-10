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
