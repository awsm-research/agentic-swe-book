# Tutorial 10: Refactor to Reduce Complexity Without Breaking Tests

A senior engineer hands you a 60-line function. The tests pass, but every reviewer who looks at it asks for changes, and the cyclomatic complexity score is in the danger zone. Your job is to keep every test green while bringing the complexity down — using three refactoring techniques that work on almost any tangled function. By the end, the function is shorter, simpler, and behaves identically.

**Concepts covered:** Cyclomatic complexity, guard clauses, lookup tables, extract function, behaviour-preserving refactoring, regression testing

**Format:** Individual or pairs | **Duration:** 2 hours | **Tool:** Python, uv, pytest, radon, Git

---

## Outline

- [Part A: Measure What You Are About to Refactor](#part-a-measure-what-you-are-about-to-refactor-60-min)
- [Part B: Refactor in Three Stages, Keeping Tests Green](#part-b-refactor-in-three-stages-keeping-tests-green-60-min)
- [References](#references)

---

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Measure cyclomatic complexity for a Python function using radon.
2. Apply guard clauses to flatten nested validation logic.
3. Replace a nested if/elif chain with a lookup table.
4. Extract small helper functions to isolate a single responsibility.
5. Verify that a behaviour-preserving refactor does not change observable output by re-running an existing test suite after every step.

---

## Part A: Measure What You Are About to Refactor *(~60 min)*

### Prerequisites

- Python 3.11+ and uv ([docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/)) — installed in Tutorial 1
- Git ([git-scm.com](https://git-scm.com/))
- VS Code ([code.visualstudio.com](https://code.visualstudio.com/))

---

### Step 1: Scaffold the Project

```bash
uv init refactor-practice
cd refactor-practice
rm hello.py
mkdir -p src tests
git init
git add pyproject.toml .python-version
git commit -m "chore: initial project setup"
```

Install pytest and radon:

```bash
uv add --dev pytest radon
```

---

### Step 2: Add the Function You Will Refactor

Create `src/shipping.py` with this deliberately complex shipping-cost calculator. The function works — it computes correct prices for a parcel given weight, destination zone, service level, and a few flags — but it does so with deeply nested branches and repeated structure.

```python
# src/shipping.py
"""Calculates parcel shipping cost. Refactor target."""


def calculate_shipping(
    weight, zone, service,
    is_member=False, has_insurance=False, is_holiday=False,
):
    if weight is None or weight <= 0:
        raise ValueError("weight must be positive")
    if zone not in (1, 2, 3, "international"):
        raise ValueError(f"invalid zone: {zone}")

    cost = 0.0
    if zone == 1:
        if service == "standard":
            cost = 5.00 + weight * 1.00
        elif service == "express":
            cost = 10.00 + weight * 1.50
        elif service == "overnight":
            cost = 20.00 + weight * 2.00
        else:
            raise ValueError(f"invalid service: {service}")
    elif zone == 2:
        if service == "standard":
            cost = 8.00 + weight * 1.20
        elif service == "express":
            cost = 14.00 + weight * 1.80
        elif service == "overnight":
            cost = 25.00 + weight * 2.50
        else:
            raise ValueError(f"invalid service: {service}")
    elif zone == 3:
        if service == "standard":
            cost = 12.00 + weight * 1.50
        elif service == "express":
            cost = 18.00 + weight * 2.20
        elif service == "overnight":
            cost = 30.00 + weight * 3.00
        else:
            raise ValueError(f"invalid service: {service}")
    elif zone == "international":
        if service == "standard":
            cost = 25.00 + weight * 3.00
        elif service == "express":
            cost = 40.00 + weight * 4.00
        elif service == "overnight":
            raise ValueError("overnight is not available internationally")
        else:
            raise ValueError(f"invalid service: {service}")

    if is_member:
        cost = cost * 0.90
    if has_insurance:
        cost = cost * 1.05
    if is_holiday:
        cost = cost * 1.20

    return round(cost, 2)
```

> **Why `weight is None or weight <= 0` and not the other way around?** Python's `or` short-circuits — if the left operand is true, the right operand is never evaluated. Putting the `None` check first means `weight <= 0` is only run for numeric values, so passing `weight=None` raises a clean `ValueError` rather than a `TypeError` from comparing `None` with `0`.

---

### Step 3: Add the Test Suite

Create `tests/test_shipping.py`. These are the tests the function currently passes. They are also the contract you must preserve through the refactor — every test must still pass after every change.

```python
# tests/test_shipping.py
import pytest
from src.shipping import calculate_shipping


# --- happy paths ---

@pytest.mark.parametrize("zone,service,weight,expected", [
    (1, "standard", 2.0, 7.00),
    (1, "express", 2.0, 13.00),
    (1, "overnight", 2.0, 24.00),
    (2, "standard", 3.0, 11.60),
    (2, "express", 3.0, 19.40),
    (3, "overnight", 1.5, 34.50),
    ("international", "standard", 5.0, 40.00),
    ("international", "express", 5.0, 60.00),
])
def test_base_costs(zone, service, weight, expected):
    assert calculate_shipping(weight, zone, service) == expected


# --- modifiers ---

def test_member_discount_applied():
    assert calculate_shipping(2.0, 1, "standard", is_member=True) == 6.30


def test_insurance_surcharge_applied():
    assert calculate_shipping(2.0, 1, "standard", has_insurance=True) == 7.35


def test_holiday_surcharge_applied():
    assert calculate_shipping(2.0, 1, "standard", is_holiday=True) == 8.40


def test_all_modifiers_combine():
    # base 7.00 -> member 6.30 -> insurance 6.615 -> holiday 7.938 -> 7.94
    assert calculate_shipping(
        2.0, 1, "standard",
        is_member=True, has_insurance=True, is_holiday=True,
    ) == 7.94


# --- error paths ---

@pytest.mark.parametrize("weight", [0, -1.0, None])
def test_invalid_weight_raises(weight):
    with pytest.raises(ValueError, match="weight must be positive"):
        calculate_shipping(weight, 1, "standard")


def test_invalid_zone_raises():
    with pytest.raises(ValueError, match="invalid zone"):
        calculate_shipping(2.0, 99, "standard")


def test_invalid_service_raises():
    with pytest.raises(ValueError, match="invalid service"):
        calculate_shipping(2.0, 1, "teleport")


def test_overnight_international_rejected():
    with pytest.raises(ValueError, match="overnight is not available"):
        calculate_shipping(2.0, "international", "overnight")
```

Run them:

```bash
uv run pytest tests/ -v
```

Expected: every test passes. If anything fails, you have a typo — fix it before continuing. The refactor is meaningless without a green baseline.

Commit the starting point:

```bash
git add src/shipping.py tests/test_shipping.py pyproject.toml uv.lock
git commit -m "feat: add shipping cost calculator with passing tests"
```

---

### Step 4: Measure Cyclomatic Complexity

Cyclomatic complexity counts the linearly independent paths through a function. Thomas McCabe proposed the metric in 1976 and recommended keeping functions below 10. Above 15 is a refactoring candidate; above 30 is a hazard.

```bash
uv run radon cc src/shipping.py -a -s
```

Expected output (the exact number depends on your Python version):

```
src/shipping.py
    F 5:0 calculate_shipping - D (17)

1 block (classes, functions, methods) analyzed.
Average complexity: D (17.0)
```

The `D (17)` rating is the cost: every nested branch adds a path that a future reader has to trace.

Record the starting numbers:

| Metric | Before |
|---|---|
| Cyclomatic complexity | 17 |
| Lines of code | ~60 |
| Tests passing | all |

---

### Step 5: Activity — Identify the Sources of Complexity

Before changing any code, write down what is making the function complex. Open `notes.md` and answer these questions:

```markdown
# Shipping Refactor — Sources of Complexity

1. How many distinct (zone, service) combinations does the function handle?
2. Which lines are *validation* and which lines are *calculation*?
3. Which sections of code are nearly identical except for numeric values?
4. Which `if` branches could be replaced by a data structure?
5. If the company adds a fourth zone, how many lines need to change?
```

Commit your answers:

```bash
git add notes.md
git commit -m "docs: identify sources of complexity in shipping function"
```

The goal of the refactor in Part B is not "make the code prettier" — it is to remove these specific sources of complexity, one at a time, while the test suite stays green.

---

## Part B: Refactor in Three Stages, Keeping Tests Green *(~60 min)*

You will apply three refactoring techniques in order. After each technique, run the tests. If anything goes red, revert and try again. The rule is non-negotiable: the test suite must be green before you start the next stage.

> **Why one technique at a time?** If you change ten things at once and a test fails, you do not know which change caused the failure. Refactoring is a sequence of small, reversible steps — each one verified before the next.

---

### Step 1: Stage 1 — Guard Clauses for Validation

A *guard clause* is an early return that handles an invalid case at the top of the function, so the rest of the function can assume valid input. The technique flattens nesting and separates validation from calculation.

The current function mixes validation with the main loop. Extract validation into a helper, called as a guard at the top of `calculate_shipping`.

Replace the contents of `src/shipping.py` with:

```python
# src/shipping.py
"""Calculates parcel shipping cost."""

VALID_ZONES = (1, 2, 3, "international")
VALID_SERVICES = ("standard", "express", "overnight")


def _validate(weight, zone, service):
    if weight is None or weight <= 0:
        raise ValueError("weight must be positive")
    if zone not in VALID_ZONES:
        raise ValueError(f"invalid zone: {zone}")
    if service not in VALID_SERVICES:
        raise ValueError(f"invalid service: {service}")
    if zone == "international" and service == "overnight":
        raise ValueError("overnight is not available internationally")


def calculate_shipping(
    weight, zone, service,
    is_member=False, has_insurance=False, is_holiday=False,
):
    _validate(weight, zone, service)

    cost = 0.0
    if zone == 1:
        if service == "standard":
            cost = 5.00 + weight * 1.00
        elif service == "express":
            cost = 10.00 + weight * 1.50
        elif service == "overnight":
            cost = 20.00 + weight * 2.00
    elif zone == 2:
        if service == "standard":
            cost = 8.00 + weight * 1.20
        elif service == "express":
            cost = 14.00 + weight * 1.80
        elif service == "overnight":
            cost = 25.00 + weight * 2.50
    elif zone == 3:
        if service == "standard":
            cost = 12.00 + weight * 1.50
        elif service == "express":
            cost = 18.00 + weight * 2.20
        elif service == "overnight":
            cost = 30.00 + weight * 3.00
    elif zone == "international":
        if service == "standard":
            cost = 25.00 + weight * 3.00
        elif service == "express":
            cost = 40.00 + weight * 4.00

    if is_member:
        cost = cost * 0.90
    if has_insurance:
        cost = cost * 1.05
    if is_holiday:
        cost = cost * 1.20

    return round(cost, 2)
```

Run the tests:

```bash
uv run pytest tests/ -v
```

Every test must still pass. If a test fails, the most likely cause is a missed validation case — re-read the original function and `_validate` side by side.

Re-measure complexity:

```bash
uv run radon cc src/shipping.py -a -s
```

Expected: complexity has dropped from `D (17)` to about `C (12)` for `calculate_shipping`, plus a small `_validate` function rated `A` or `B`. The validation paths still exist; they are just no longer tangled with the calculation.

Commit:

```bash
git add src/shipping.py
git commit -m "refactor: extract validation as a guard clause"
```

---

### Step 2: Stage 2 — Replace if/elif Chain with a Lookup Table

The middle of the function is a 3 × 4 grid of (zone, service) → (base, per_kg) values, expressed as twelve nested branches. A dictionary expresses the same information as data.

Replace `src/shipping.py` with:

```python
# src/shipping.py
"""Calculates parcel shipping cost."""

VALID_ZONES = (1, 2, 3, "international")
VALID_SERVICES = ("standard", "express", "overnight")

# (zone, service) -> (base_fee, per_kg)
RATES = {
    (1, "standard"): (5.00, 1.00),
    (1, "express"): (10.00, 1.50),
    (1, "overnight"): (20.00, 2.00),
    (2, "standard"): (8.00, 1.20),
    (2, "express"): (14.00, 1.80),
    (2, "overnight"): (25.00, 2.50),
    (3, "standard"): (12.00, 1.50),
    (3, "express"): (18.00, 2.20),
    (3, "overnight"): (30.00, 3.00),
    ("international", "standard"): (25.00, 3.00),
    ("international", "express"): (40.00, 4.00),
}


def _validate(weight, zone, service):
    if weight is None or weight <= 0:
        raise ValueError("weight must be positive")
    if zone not in VALID_ZONES:
        raise ValueError(f"invalid zone: {zone}")
    if service not in VALID_SERVICES:
        raise ValueError(f"invalid service: {service}")
    if zone == "international" and service == "overnight":
        raise ValueError("overnight is not available internationally")


def calculate_shipping(
    weight, zone, service,
    is_member=False, has_insurance=False, is_holiday=False,
):
    _validate(weight, zone, service)

    base, per_kg = RATES[(zone, service)]
    cost = base + weight * per_kg

    if is_member:
        cost = cost * 0.90
    if has_insurance:
        cost = cost * 1.05
    if is_holiday:
        cost = cost * 1.20

    return round(cost, 2)
```

Run the tests:

```bash
uv run pytest tests/ -v
```

All tests must still pass. The `RATES` table contains exactly the same numbers as the original branches — adding a new zone or service is now a one-line dictionary entry instead of a new `elif` block.

Re-measure complexity:

```bash
uv run radon cc src/shipping.py -a -s
```

Expected: `calculate_shipping` is now around `A (5)` — well below McCabe's threshold. The complexity has gone into the data, where it belongs.

Commit:

```bash
git add src/shipping.py
git commit -m "refactor: replace if/elif rate chain with lookup table"
```

---

### Step 3: Stage 3 — Extract a Helper for the Modifiers

The three modifier flags at the end of the function are doing one job — applying multiplicative adjustments. Extract them so each function does one thing.

Replace `src/shipping.py` with:

```python
# src/shipping.py
"""Calculates parcel shipping cost."""

VALID_ZONES = (1, 2, 3, "international")
VALID_SERVICES = ("standard", "express", "overnight")

RATES = {
    (1, "standard"): (5.00, 1.00),
    (1, "express"): (10.00, 1.50),
    (1, "overnight"): (20.00, 2.00),
    (2, "standard"): (8.00, 1.20),
    (2, "express"): (14.00, 1.80),
    (2, "overnight"): (25.00, 2.50),
    (3, "standard"): (12.00, 1.50),
    (3, "express"): (18.00, 2.20),
    (3, "overnight"): (30.00, 3.00),
    ("international", "standard"): (25.00, 3.00),
    ("international", "express"): (40.00, 4.00),
}


def _validate(weight, zone, service):
    if weight is None or weight <= 0:
        raise ValueError("weight must be positive")
    if zone not in VALID_ZONES:
        raise ValueError(f"invalid zone: {zone}")
    if service not in VALID_SERVICES:
        raise ValueError(f"invalid service: {service}")
    if zone == "international" and service == "overnight":
        raise ValueError("overnight is not available internationally")


def _apply_modifiers(cost, is_member, has_insurance, is_holiday):
    if is_member:
        cost *= 0.90
    if has_insurance:
        cost *= 1.05
    if is_holiday:
        cost *= 1.20
    return cost


def calculate_shipping(
    weight, zone, service,
    is_member=False, has_insurance=False, is_holiday=False,
):
    _validate(weight, zone, service)
    base, per_kg = RATES[(zone, service)]
    cost = base + weight * per_kg
    cost = _apply_modifiers(cost, is_member, has_insurance, is_holiday)
    return round(cost, 2)
```

Run the tests one more time:

```bash
uv run pytest tests/ -v
```

Re-measure:

```bash
uv run radon cc src/shipping.py -a -s
```

Expected output:

```
src/shipping.py
    F 22:0 _validate - A (5)
    F 33:0 _apply_modifiers - A (4)
    F 43:0 calculate_shipping - A (1)

3 blocks (classes, functions, methods) analyzed.
Average complexity: A (3.3)
```

The main function is now `A (1)` — every operation it performs is a single named step. Complexity has not vanished; it has been distributed across small, single-purpose functions, each with a complexity that fits in a reader's head.

Commit:

```bash
git add src/shipping.py
git commit -m "refactor: extract modifier application into helper"
```

---

### Step 4: Record the Before-and-After

Update `notes.md`:

```markdown
# Shipping Refactor — Results

| Metric | Before | After |
|---|---|---|
| `calculate_shipping` cyclomatic complexity | 17 | 1 |
| Number of functions | 1 | 3 |
| Lines in `calculate_shipping` body | ~50 | ~6 |
| Tests passing | 17 / 17 | 17 / 17 |
| Behaviour changed | — | no |

## Adding a new zone now requires
- Before: a new `elif zone == X` block with three nested service branches (~12 lines)
- After: one entry per service in `RATES` (3 lines), plus updating `VALID_ZONES`
```

Commit:

```bash
git add notes.md
git commit -m "docs: record before/after complexity measurements"
```

---

### Step 5: Activity — Refactor a Second Function on Your Own

Add this second high-complexity function to `src/shipping.py` and a small test suite for it. Then refactor it using the three techniques from this tutorial. The complexity target is `A (≤ 5)` while keeping every test green.

```python
# src/shipping.py — append

def estimate_delivery_days(zone, service, is_holiday=False, is_remote=False):
    if zone is None or service is None:
        raise ValueError("zone and service required")
    if zone == 1:
        if service == "standard":
            days = 3
        elif service == "express":
            days = 2
        elif service == "overnight":
            days = 1
        else:
            raise ValueError(f"invalid service: {service}")
    elif zone == 2:
        if service == "standard":
            days = 5
        elif service == "express":
            days = 3
        elif service == "overnight":
            days = 1
        else:
            raise ValueError(f"invalid service: {service}")
    elif zone == 3:
        if service == "standard":
            days = 7
        elif service == "express":
            days = 4
        elif service == "overnight":
            days = 2
        else:
            raise ValueError(f"invalid service: {service}")
    elif zone == "international":
        if service == "standard":
            days = 14
        elif service == "express":
            days = 7
        elif service == "overnight":
            raise ValueError("overnight is not available internationally")
        else:
            raise ValueError(f"invalid service: {service}")
    else:
        raise ValueError(f"invalid zone: {zone}")

    if is_holiday:
        days += 2
    if is_remote:
        days += 3
    return days
```

```python
# tests/test_shipping.py — append
from src.shipping import estimate_delivery_days


@pytest.mark.parametrize("zone,service,expected_days", [
    (1, "standard", 3),
    (1, "overnight", 1),
    (2, "express", 3),
    (3, "standard", 7),
    ("international", "express", 7),
])
def test_delivery_days(zone, service, expected_days):
    assert estimate_delivery_days(zone, service) == expected_days


def test_delivery_days_holiday_adds_two():
    assert estimate_delivery_days(1, "standard", is_holiday=True) == 5


def test_delivery_days_remote_adds_three():
    assert estimate_delivery_days(1, "standard", is_remote=True) == 6


def test_delivery_days_invalid_zone():
    with pytest.raises(ValueError, match="invalid zone"):
        estimate_delivery_days(99, "standard")


def test_delivery_days_overnight_international_rejected():
    with pytest.raises(ValueError):
        estimate_delivery_days("international", "overnight")
```

Verify the starting state — tests pass and complexity is high:

```bash
uv run pytest tests/ -v
uv run radon cc src/shipping.py -a -s
```

Now refactor `estimate_delivery_days` using the same three stages:

1. **Guard clauses** — extract validation (you can reuse or extend `_validate`).
2. **Lookup table** — replace the nested `if`/`elif` with a `(zone, service) -> days` dictionary.
3. **Extract function** — pull the holiday/remote modifier logic into a small helper.

After each stage:

```bash
uv run pytest tests/ -v
uv run radon cc src/shipping.py -a -s
```

When `estimate_delivery_days` is at `A (≤ 5)` and every test still passes, commit:

```bash
git add src/shipping.py tests/test_shipping.py
git commit -m "refactor: simplify estimate_delivery_days using lookup table"
```

You have now applied the same three-stage workflow twice. This is the rhythm of safe refactoring: small steps, verified by tests, never more than one technique at a time.

---

## References

- [radon Documentation](https://radon.readthedocs.io/) — cyclomatic complexity, maintainability index, and Halstead metrics for Python
- [pytest Documentation](https://docs.pytest.org/) — test runner, fixtures, and parametrize
- [Refactoring Catalog (Martin Fowler)](https://refactoring.com/catalog/) — the canonical catalogue of refactoring moves, including Replace Conditional with Lookup, Extract Function, and Guard Clauses
- [Cyclomatic Complexity (McCabe, 1976)](https://ieeexplore.ieee.org/document/1702388) — original paper introducing the metric
- [Working Effectively with Legacy Code](https://www.oreilly.com/library/view/working-effectively-with/0131177052/) — Michael Feathers on safe behaviour-preserving refactoring
