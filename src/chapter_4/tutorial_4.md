## 4.7 Tutorial: Unit Testing in Practice

You have a function that calculates tax deductions — but you cannot trust it until you have tested it, measured the coverage, and confirmed every decision branch has been exercised. This tutorial builds that test suite from scratch: you will write the initial tests, run statement and branch coverage reports, identify the gaps, and close them until the suite reaches 100% branch coverage.

**Concepts covered:** unit testing with `unittest`, Arrange–Act–Assert pattern, statement coverage, branch coverage, `pytest-cov`

**Format:** Individual or pairs | **Duration:** ~1 hour | **Tool:** Python, pytest, pytest-cov

---

### Outline

- [Part A: Build the Initial Test Suite](#part-a-build-the-initial-test-suite-35-min)
- [Part B: Measure and Close Coverage Gaps](#part-b-measure-and-close-coverage-gaps-25-min)
- [References](#references)

---

### Learning Objectives

- Write unit tests using `unittest.TestCase` assertion methods with the Arrange–Act–Assert (AAA) pattern
- Run `pytest-cov` statement and branch coverage reports and interpret their output
- Iteratively close coverage gaps until the test suite reaches 100% branch coverage

---

### Part A: Build the Initial Test Suite *(~35 min)*

#### Step 1: The Scenario

You are writing a tax deduction calculator for the Australian Taxation Office (ATO). Given a taxpayer's income, age, and personal circumstances, the function returns the total deduction amount they qualify for under the following hypothetical rules:

| Rule | Condition | Deduction |
|---|---|---|
| Low income (full) | `income ≤ $18,200` | +$700 |
| Low income (partial) | `$18,200 < income ≤ $37,000` | +$300 |
| Senior supplement | `age ≥ 67` | +$400 |
| Spouse offset | `has_spouse == True` | +$200 |
| Disability supplement | `disabled == True` | +$600 |
| Invalid input | `income < 0` | raise `ValueError` |

**Production code:**

```python
# src/tax.py

LOW_INCOME_THRESHOLD = 18_200
MID_INCOME_THRESHOLD = 37_000
SENIOR_AGE = 67


def calculate_deduction(
    income: float,
    age: int,
    has_spouse: bool,
    disabled: bool,
) -> float:
    """Calculate the ATO tax deduction for a taxpayer.

    Args:
        income: Annual taxable income in AUD.
        age: Taxpayer's age in years.
        has_spouse: True if the taxpayer claims the spouse offset.
        disabled: True if the taxpayer claims the disability supplement.

    Returns:
        Total deduction amount in AUD.

    Raises:
        ValueError: If income is negative.
    """
    if income < 0:
        raise ValueError("Income cannot be negative")

    deduction = 0.0

    if income <= LOW_INCOME_THRESHOLD:
        deduction += 700.0
    elif income <= MID_INCOME_THRESHOLD:
        deduction += 300.0

    if age >= SENIOR_AGE:
        deduction += 400.0

    if has_spouse:
        deduction += 200.0

    if disabled:
        deduction += 600.0

    return deduction
```

The function contains six decision points — one True branch and one False branch per condition — giving twelve branches in total:

| Decision point | Condition | True branch | False branch |
|---|---|---|---|
| Validation | `income < 0` | raise `ValueError` | continue |
| Low income | `income <= 18,200` | add $700 | check next |
| Mid income | `income <= 37,000` | add $300 | no supplement |
| Senior age | `age >= 67` | add $400 | no supplement |
| Spouse | `has_spouse` | add $200 | no supplement |
| Disability | `disabled` | add $600 | no supplement |

---

#### Step 2: Assertion Methods in `unittest`

All tests in this tutorial use `unittest.TestCase`. Each method produces a descriptive failure message automatically — you do not need to write one.

| Method | What it checks |
|--------|----------------|
| `self.assertEqual(a, b)` | exact equality |
| `self.assertAlmostEqual(a, b, places=2)` | float equality within tolerance |
| `self.assertGreater(a, b)` | `a > b` |
| `self.assertGreaterEqual(a, b)` | `a >= b` |
| `self.assertLess(a, b)` | `a < b` |
| `self.assertIsInstance(a, T)` | runtime type |
| `self.assertIsNotNone(a)` | value is not `None` |
| `self.assertRaises(Exc)` | expected exception type |
| `self.assertRaisesRegex(Exc, pattern)` | expected exception and message |

---

#### Step 3: Write the Initial Test Suite

Each test follows the **Arrange–Act–Assert** pattern: set up inputs, call the function, verify the output.

```python
# tests/test_tax.py
import unittest
from src.tax import calculate_deduction


class TestCalculateDeduction(unittest.TestCase):

    def test_no_supplements_above_mid_income(self) -> None:
        # Arrange
        income = 50_000.0
        age = 40
        has_spouse = False
        disabled = False

        # Act
        result = calculate_deduction(income, age, has_spouse, disabled)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result, 0.0)
        self.assertIsInstance(result, float)

    def test_full_low_income_supplement(self) -> None:
        # Arrange
        income = 15_000.0
        age = 40
        has_spouse = False
        disabled = False

        # Act
        result = calculate_deduction(income, age, has_spouse, disabled)

        # Assert
        self.assertEqual(result, 700.0)

    def test_senior_supplement(self) -> None:
        # Arrange
        income = 50_000.0
        age = 70
        has_spouse = False
        disabled = False

        # Act
        result = calculate_deduction(income, age, has_spouse, disabled)

        # Assert
        self.assertEqual(result, 400.0)
        self.assertGreater(result, 0)

    def test_spouse_offset(self) -> None:
        # Arrange
        income = 50_000.0
        age = 40
        has_spouse = True
        disabled = False

        # Act
        result = calculate_deduction(income, age, has_spouse, disabled)

        # Assert
        self.assertEqual(result, 200.0)

    def test_disability_supplement(self) -> None:
        # Arrange
        income = 50_000.0
        age = 40
        has_spouse = False
        disabled = True

        # Act
        result = calculate_deduction(income, age, has_spouse, disabled)

        # Assert
        self.assertEqual(result, 600.0)

    def test_all_supplements_combined(self) -> None:
        # Arrange — taxpayer qualifies for every supplement
        income = 10_000.0   # below LOW_INCOME_THRESHOLD → +$700
        age = 70            # above SENIOR_AGE           → +$400
        has_spouse = True   #                              +$200
        disabled = True     #                              +$600

        # Act
        result = calculate_deduction(income, age, has_spouse, disabled)

        # Assert — expected total: 700 + 400 + 200 + 600 = 1900
        self.assertAlmostEqual(result, 1_900.0, places=2)
        self.assertGreaterEqual(result, 1_000.0)
```

---

#### Step 4: Activity — Run the Suite and Confirm All Tests Pass

Run the suite in verbose mode. For each of the six tests, identify which row in the branch table from Step 1 it exercises.

```bash
pytest tests/test_tax.py -v
```

<details>
<summary>Expected output</summary>

```
tests/test_tax.py::TestCalculateDeduction::test_no_supplements_above_mid_income PASSED
tests/test_tax.py::TestCalculateDeduction::test_full_low_income_supplement PASSED
tests/test_tax.py::TestCalculateDeduction::test_senior_supplement PASSED
tests/test_tax.py::TestCalculateDeduction::test_spouse_offset PASSED
tests/test_tax.py::TestCalculateDeduction::test_disability_supplement PASSED
tests/test_tax.py::TestCalculateDeduction::test_all_supplements_combined PASSED

6 passed in 0.XXs
```

All six tests pass. Notice that not every branch table row has a test that exercises it exclusively — `test_all_supplements_combined` exercises four True branches at once. Coverage analysis in Part B will show exactly which branches remain untested.

</details>

---

### Part B: Measure and Close Coverage Gaps *(~25 min)*

#### Step 1: Install pytest-cov

`pytest-cov` extends pytest with statement and branch coverage reporting. Install it as a development dependency:

```bash
uv add --dev pytest-cov
```

---

#### Step 2: Activity — Predict and Verify Statement Coverage

`pytest-cov` measures which statements in `tax.py` are executed by the test suite. Before running the command below, look at the six tests and the branch table in Step 1 of Part A. Which lines do you predict will be missing?

```bash
pytest tests/test_tax.py --cov=src --cov-report=term-missing -q
```

<details>
<summary>Expected output</summary>

```
Name         Stmts   Miss  Cover   Missing
------------------------------------------
src/tax.py      12      2    83%   27, 34
------------------------------------------
TOTAL           12      2    83%
```

Two lines are never executed:

| Line | Statement | Why it is missed |
|------|-----------|-----------------|
| 27 | `raise ValueError("Income cannot be negative")` | No test passes a negative income |
| 34 | `deduction += 300.0` | No test uses an income between $18,200 and $37,000 |

</details>

---

#### Step 3: Check Branch Coverage

Statement coverage tells you whether a line was *ever* executed — not whether every *decision* was exercised in both directions. Enable branch coverage to see the full picture:

```bash
pytest tests/test_tax.py --cov=src --cov-branch --cov-report=term-missing -q
```

---

#### Step 4: Activity — Compare Statement and Branch Coverage

What additional information does the branch coverage report reveal compared to statement coverage?

<details>
<summary>Expected output</summary>

```
Name         Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------
src/tax.py      12      2      12      2    83%   27, 34
---------------------------------------------------------
TOTAL           12      2      12      2    83%
```

| Column | Meaning |
|--------|---------|
| `Branch` | Total conditional outcomes in the file (6 decisions × 2 = 12) |
| `BrPart` | Decision points where one direction is never exercised |
| `Cover` | Combined statement + branch percentage |

`BrPart = 2` means two decision points each have one direction that no test ever takes. In this function, every missing statement is also a missing branch — the two gaps are identical. This will not always be the case: once a branch leads to no new code (e.g., an empty `else` block), branch coverage can catch what statement coverage cannot.

</details>

---

#### Step 5: Activity — Write Tests for the Missing Branches

Write one test for each missing branch. Use the branch table in Step 1 of Part A to identify what input values would trigger each uncovered condition.

When a function is expected to raise an exception, Act and Assert merge into a single `with self.assertRaises(...)` block — the exception itself is the output being verified.

<details>
<summary>Solution</summary>

```python
# Append to class TestCalculateDeduction in tests/test_tax.py

    def test_negative_income_raises_value_error(self) -> None:
        # Arrange
        income = -500.0
        age = 40
        has_spouse = False
        disabled = False

        # Act & Assert — exception is the expected output
        with self.assertRaisesRegex(ValueError, "cannot be negative"):
            calculate_deduction(income, age, has_spouse, disabled)

    def test_mid_income_partial_supplement(self) -> None:
        # Arrange — income sits between the two thresholds
        income = 25_000.0   # 18,200 < 25,000 ≤ 37,000 → +$300
        age = 40
        has_spouse = False
        disabled = False

        # Act
        result = calculate_deduction(income, age, has_spouse, disabled)

        # Assert
        self.assertEqual(result, 300.0)
        self.assertLess(result, 700.0)      # partial, not full low-income supplement
```

Re-run with branch coverage to confirm 100%:

```bash
pytest tests/test_tax.py --cov=src --cov-branch --cov-report=term-missing -q
```

```
Name         Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------
src/tax.py      12      0      12      0   100%
---------------------------------------------------------
TOTAL           12      0      12      0   100%
```

Every statement is executed and every decision point is exercised in both directions.

</details>

> **Reflection:** Eight tests and 100% branch coverage do not prove the deduction logic is correct — they prove it behaves *as written*. If the low-income threshold were typed as `18_000` instead of `18_200`, all tests would still pass as long as the test data did not land in the gap. Coverage identifies *untested* code; meaningful assertions on the *right* boundary values are what catch bugs.

---

### References

- [Python `unittest` Documentation](https://docs.python.org/3/library/unittest.html) — Built-in test framework: `TestCase`, assertion methods, and test discovery
- [pytest Documentation](https://docs.pytest.org/) — Test runner used throughout this tutorial; compatible with `unittest.TestCase` subclasses
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/) — Statement and branch coverage reporting with pytest; `--cov`, `--cov-branch`, and `--cov-report` flags
- [Coverage.py Documentation](https://coverage.readthedocs.io/) — The underlying coverage engine; explains how statement and branch coverage are measured
