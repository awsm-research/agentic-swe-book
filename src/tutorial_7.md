# Tutorial 7: The AI-Assisted SDLC: From Code to Well-Tested App

The `AssignJobService` you built in Tutorial 6 is implemented and reviewed — but is it correct, and can it survive the first maintenance cycle? This tutorial answers both questions. You will use an AI agent to generate and evaluate a test suite, then use it to catch a real bug — and finally evolve the design when a requirement changes.

**Concepts covered:** AI-generated test suite evaluation, assertion quality, coverage-driven refinement, AI-assisted debugging, requirement evolution, Strategy pattern

**Format:** Individual | **Duration:** 90 min | **Tool:** AI Assistant (Claude Code)

---

## Outline

- [The Scenario](#the-scenario)
- [Activity 1 — AI for Testing](#activity-1--ai-for-testing)
- [Activity 2 — AI for Maintenance](#activity-2--ai-for-maintenance)
- [References](#references)

---

## Learning Objectives

By the end of this tutorial, you will be able to:

1. Generate a complete pytest test suite for an AI-produced service using a structured prompt.
2. Evaluate AI-generated tests against four quality criteria: assertion strength, boundary coverage, notification verification, and test isolation.
3. Identify gaps in an AI-generated test suite using coverage analysis and write targeted tests by hand to fill them.
4. Distinguish between specification gaps and AI failures when tests miss edge cases.
5. Use an AI agent to diagnose a bug from a failing test, identify its root cause, and apply a minimal fix.
6. Direct an AI agent to perform a change impact analysis when a requirement evolves.
7. Apply the Strategy pattern to decouple a service from a concrete implementation, guided by AI-produced code and critiqued against SOLID principles.

---

## Prerequisites

- Completed Tutorial 6 — `src/service/job_service.py` is in place with the `AssignJobService` implementation
- pytest and pytest-cov installed in the project: `uv add pytest pytest-cov`
- Claude Code CLI open in the project directory ([Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code)); a conversational AI assistant works if Claude Code is unavailable

---

## The Scenario

This tutorial continues with the Field Repair Tracker from Tutorial 6. The `AssignJobService.assign` method has been generated and reviewed — it enforces the business rules from the spec, uses dependency injection, and sends notifications asynchronously. The question now is whether the implementation actually does what it claims: does it raise the right exception for each error condition, and is the notification truly not sent when the assignment fails?

---

## Activity 1 — AI for Testing *(~45 min)*

**Concepts covered:** Test generation, test quality evaluation, coverage analysis

In Chapter 4, you learned to write unit tests with pytest, to evaluate coverage, and to critically assess AI-generated tests. In this activity, you will use AI Assistant to generate a full unit test suite for the `AssignJobService` — and then apply the evaluation criteria from Chapter 4, §4.9.3 to assess its quality.

### Step 1: Generate the Test Suite *(~10 min)*

In your AI Assistant session, give the following prompt:

<div class="admonish-prompt">

Read `src/service/job_service.py`. Generate a complete pytest test suite in `tests/test_job_service.py` for the AssignJobService.assign method. Requirements for the test suite:

1. Use pytest fixtures for all shared setup (mock repository, mock notification service, sample job, sample technician)
2. Cover all business rules from the specification: happy path, job not found (404), technician not found (409), technician not available (409), caller not a manager (403)
3. Verify that the notification service is called exactly once on a successful assignment
4. Verify that the notification service is NOT called when assignment fails
5. Use unittest.mock.MagicMock for all external dependencies — do not use a real database
6. Each test method name must describe the scenario it tests (not 'test_1', 'test_assign', etc.)

</div>

### Step 2: Evaluate the Generated Tests *(~15 min)*

Apply the evaluation checklist from Chapter 4, §4.9.3 to the AI-generated suite:

**1. Does each test assert something meaningful?**

Look for tests that call `assign(...)` and only assert `result is not None`. These provide no value. Every test should assert a specific outcome: the returned job has the correct status, the repository's `update_assignee` was called with the correct arguments, or a specific exception was raised.

**2. Are the boundary cases covered?**

The specification has three error conditions. Count how many the AI tested. If any are missing, add them manually — do not ask the AI to fix this, so you can experience the gap directly.

**3. Is the notification call verified correctly?**

A common AI mistake is to assert `mock_notifier.send.assert_called()` (was it called at all?) rather than `mock_notifier.send.assert_called_once_with(expected_email, expected_message)`. The latter is a much stronger assertion.

**4. Are the tests isolated?**

Check that no test depends on the order in which tests run. If a fixture is modified inside a test (e.g., a list is appended to), subsequent tests may receive different state.

> See [Sample Answer: Activity 1 — Unit Test Suite](#sample-answer-activity-1--unit-test-suite) at the end of this tutorial.

### Step 3: Activity — Analyse Coverage and Refine *(~20 min)*

Run the test suite with coverage:

```bash
pytest tests/test_job_service.py -v --cov=src/service --cov-report=term-missing
```

If coverage is below 90% for `job_service.py`, identify the uncovered lines and ask the AI to explain what scenario each uncovered line represents. Then write a test for each gap — by hand, not by AI — so you experience what it means to design a test for a specific scenario rather than generate tests in bulk.

**After completing this tutorial, consider:**

1. **Where did AI save the most time?** Generating boilerplate (fixtures, mock setup, happy-path tests) is typically where AI provides the highest leverage.
2. **Where did AI create the most risk?** Missing boundary conditions, weak assertions (`assert_called()` instead of `assert_called_once_with(...)`), and absent negative assertions are the most common gaps — and every gap maps to something the specification left implicit.
3. **Which error condition did your AI miss, and why?** Was it a specification gap (the spec never stated what happens when the technician is not found vs. not available) or a generation failure (the scenario was clearly specified but the AI skipped it)? The distinction matters: specification gaps require a better spec; generation failures require a better prompt.
4. **If a hand-written test fails, how do you determine whether the test is wrong or the implementation is wrong?** Write down your reasoning before checking the source code.

---

## Activity 2 — AI for Maintenance *(~45 min)*

**Concepts covered:** AI-assisted debugging, requirement evolution, Strategy pattern

A feature is never finished at the first merge. In Chapter 1, you saw that maintenance dominates the SDLC — real systems spend more time being changed than being built. In this activity, the `AssignJobService` survives its first maintenance cycle: a failing test reveals a persistence bug, a product requirement expands the notification channels, and the design needs to evolve without breaking what already works.

### Step 1: Diagnose and Fix a Bug *(~15 min)*

After deployment, the ops team reports that jobs appear assigned in API responses (the endpoint returns 200 and the job object shows `status: "assigned"`) — but overnight database queries show jobs still as UNASSIGNED. The `update_assignee` call does not raise an exception, but the `status` column is not being updated.

Give AI Assistant the following prompt:

<div class="admonish-prompt">

Here is a bug report: `POST /jobs/{id}/assign` returns 200 and the response body shows `status: "assigned"`, but a direct database query confirms the `status` column is not changing.

Read `src/service/job_service.py` and `src/repository/job_repository.py`. Diagnose the root cause. Is the status update missing from the repository method, the service method, or the domain model? Show the minimal fix — change only the code that is wrong, not the surrounding structure.

</div>

**Review the fix against this checklist:**

| Check | What to look for |
|---|---|
| **Root cause identified** | Does the AI correctly locate the missing `status` update in the repository's SQL or ORM call? |
| **Minimal change** | Does the fix touch only `update_assignee` (and its test), not the service or domain model? |
| **Test updated** | Does the AI update `test_assigns_job_to_available_technician` to assert `status == ASSIGNED` in the database, not just in the returned object? |
| **No regression** | Do all existing tests still pass after the fix? |

> **What this bug reveals:** The AI generated code that was consistent with itself (service sets status on the domain object, test checks the domain object) but inconsistent with the real persistence contract (the database was never told). AI-generated tests that mock the repository cannot catch this class of bug — only integration tests that query a real database can.

### Step 2: Evolve the Requirement *(~10 min)*

The product owner arrives with new requirements: technicians should be able to choose between push notifications and email notifications. The assignment notification must use the technician's preferred channel.

Ask AI Assistant to analyse the impact before writing any code:

<div class="admonish-prompt">

The notification requirement has changed. Previously: always send a push notification on assignment. New requirement: send the notification via the technician's preferred channel. The `Technician` domain model will carry a new `notification_preference` field (enum: `PUSH`, `EMAIL`).

Given the current implementation in `src/service/job_service.py`, `src/domain/repair_job.py`, and `src/repository/job_repository.py`, produce a change impact analysis:
1. Which classes and methods must change?
2. Which tests must be updated or added?
3. What is the risk of adding an `if notification_preference == PUSH` branch directly inside `AssignJobService.assign`?
4. What design pattern would eliminate that risk?

Do not write implementation code yet.

</div>

**Check your output:** Does the AI's impact analysis mention the Open/Closed Principle? Does it recommend the Strategy pattern (or equivalent) unprompted? If it only lists files to change without naming the design risk, prompt it to "identify which SOLID principle an `if`-branch approach would violate."

### Step 3: Activity — Apply the Strategy Pattern *(~20 min)*

With the impact analysis in hand, direct AI Assistant to make the change:

<div class="admonish-prompt">

Refactor the notification logic using the Strategy pattern:

1. Create an abstract base class `NotificationStrategy` in `src/notification/strategy.py` with a single method `send(recipient: str, message: str) -> None`.
2. Create `PushNotificationStrategy` and `EmailNotificationStrategy` as concrete implementations.
3. Update `AssignJobService` so it depends on `NotificationStrategy` (injected), not on `PushNotificationService` directly. Do not add any `if` branch to `assign`.
4. Add a factory function `get_notification_strategy(preference: NotificationPreference) -> NotificationStrategy` in `src/notification/factory.py`.
5. Update the test fixtures in `tests/test_job_service.py` to inject a `MagicMock(spec=NotificationStrategy)`.

Follow the existing type annotation style. Do not change the `assign` method's public signature.

</div>

Review the generated refactoring against the following checklist. For any item that fails, use a follow-up prompt to fix it:

| Check | What to look for |
|---|---|
| **OCP compliance** | Adding `SmsNotificationStrategy` should require only a new file — no changes to `AssignJobService` |
| **DIP compliance** | `AssignJobService` imports `NotificationStrategy` (abstract), not any concrete class |
| **Strategy selection outside the service** | The `if preference == PUSH` logic is in `factory.py`, not in `assign` |
| **Test fixture updated** | `mock_notifier` is replaced with `MagicMock(spec=NotificationStrategy)` — the spec catches calls to non-existent methods |
| **No regression** | All existing tests pass; new tests cover both `PushNotificationStrategy` and `EmailNotificationStrategy` |

If the AI placed strategy selection inside `assign`, use this correction prompt:

<div class="admonish-prompt">

The strategy selection inside `assign` violates the Open/Closed Principle — every new channel requires editing the service. Move the selection to `factory.py` so that `AssignJobService.assign` receives an already-resolved strategy and never needs to change when a new channel is added.

</div>

---

## Tutorial Summary

AI generates a plausible first draft of a test suite quickly — but plausible is not correct. The gaps it leaves map precisely to what the specification left implicit. And when a requirement changes, AI can produce the new implementation — but it needs a human to name the design constraint (the Open/Closed Principle, the Strategy pattern) before it produces a design that doesn't rot.

---

## Sample Answers

*Attempt the activity fully before expanding this answer. The value comes from comparing your AI's output against a reference — not from reading the reference first.*

---

### Sample Answer: Activity 1 — Unit Test Suite

<details>
<summary>Click to reveal sample pytest test suite for AssignJobService</summary>

```python
# tests/test_job_service.py
import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from src.service.job_service import AssignJobService, JobNotFoundError, PermissionDeniedError, TechnicianNotAvailableError
from src.domain.repair_job import RepairJob, Technician, StatusEnum, AvailabilityEnum


@pytest.fixture
def mock_job_repo():
    return MagicMock()


@pytest.fixture
def mock_tech_repo():
    return MagicMock()


@pytest.fixture
def mock_notifier():
    return MagicMock()


@pytest.fixture
def service(mock_job_repo, mock_tech_repo, mock_notifier):
    return AssignJobService(
        job_repo=mock_job_repo,
        tech_repo=mock_tech_repo,
        notifier=mock_notifier,
    )


@pytest.fixture
def available_technician():
    return Technician(
        id=uuid4(),
        name="Alex Chen",
        email="alex@fieldco.com",
        availability=AvailabilityEnum.AVAILABLE,
    )


@pytest.fixture
def unassigned_job():
    return RepairJob(
        id=uuid4(),
        site_address="123 Main St",
        fault_description="Power outage",
        priority="high",
        status=StatusEnum.UNASSIGNED,
    )


class TestAssignJob:
    def test_assigns_job_to_available_technician(
        self, service, mock_job_repo, mock_tech_repo,
        unassigned_job, available_technician
    ) -> None:
        mock_job_repo.find_by_id.return_value = unassigned_job
        mock_tech_repo.find_by_email.return_value = available_technician

        result = service.assign(job_id=unassigned_job.id, assignee_email="alex@fieldco.com")

        assert result.status == StatusEnum.ASSIGNED
        assert result.assignee_id == available_technician.id
        mock_job_repo.update_assignee.assert_called_once_with(
            unassigned_job.id, available_technician.id
        )

    def test_sends_notification_on_successful_assignment(
        self, service, mock_job_repo, mock_tech_repo, mock_notifier,
        unassigned_job, available_technician
    ) -> None:
        mock_job_repo.find_by_id.return_value = unassigned_job
        mock_tech_repo.find_by_email.return_value = available_technician

        service.assign(job_id=unassigned_job.id, assignee_email="alex@fieldco.com")

        mock_notifier.send.assert_called_once_with(
            recipient="alex@fieldco.com",
            message=f"You have been assigned job {unassigned_job.id}",
        )

    def test_raises_job_not_found_when_job_does_not_exist(
        self, service, mock_job_repo
    ) -> None:
        mock_job_repo.find_by_id.return_value = None

        with pytest.raises(JobNotFoundError):
            service.assign(job_id=uuid4(), assignee_email="alex@fieldco.com")

    def test_does_not_send_notification_when_job_not_found(
        self, service, mock_job_repo, mock_notifier
    ) -> None:
        mock_job_repo.find_by_id.return_value = None

        with pytest.raises(JobNotFoundError):
            service.assign(job_id=uuid4(), assignee_email="alex@fieldco.com")

        mock_notifier.send.assert_not_called()

    def test_raises_permission_denied_when_caller_is_not_a_manager(
        self, service
    ) -> None:
        with pytest.raises(PermissionDeniedError):
            service.assign(
                job_id=uuid4(),
                assignee_email="alex@fieldco.com",
                caller_role="technician",
            )

    def test_raises_technician_not_available_when_technician_not_found(
        self, service, mock_job_repo, mock_tech_repo, unassigned_job
    ) -> None:
        mock_job_repo.find_by_id.return_value = unassigned_job
        mock_tech_repo.find_by_email.return_value = None

        with pytest.raises(TechnicianNotAvailableError):
            service.assign(job_id=unassigned_job.id, assignee_email="unknown@fieldco.com")

    def test_raises_technician_not_available_when_on_leave(
        self, service, mock_job_repo, mock_tech_repo, unassigned_job
    ) -> None:
        on_leave_tech = Technician(
            id=uuid4(),
            name="Sam Rivera",
            email="sam@fieldco.com",
            availability=AvailabilityEnum.ON_LEAVE,
        )
        mock_job_repo.find_by_id.return_value = unassigned_job
        mock_tech_repo.find_by_email.return_value = on_leave_tech

        with pytest.raises(TechnicianNotAvailableError):
            service.assign(job_id=unassigned_job.id, assignee_email="sam@fieldco.com")

    def test_does_not_send_notification_when_technician_not_available(
        self, service, mock_job_repo, mock_tech_repo, mock_notifier, unassigned_job
    ) -> None:
        on_leave_tech = Technician(
            id=uuid4(),
            name="Sam Rivera",
            email="sam@fieldco.com",
            availability=AvailabilityEnum.ON_LEAVE,
        )
        mock_job_repo.find_by_id.return_value = unassigned_job
        mock_tech_repo.find_by_email.return_value = on_leave_tech

        with pytest.raises(TechnicianNotAvailableError):
            service.assign(job_id=unassigned_job.id, assignee_email="sam@fieldco.com")

        mock_notifier.send.assert_not_called()
```

**What to look for in your own output:**
- Does your AI generate `assert result is not None` instead of `assert result.status == StatusEnum.ASSIGNED`? The former passes even if the assignment logic sets the wrong status.
- Does your AI use `assert_called()` instead of `assert_called_once_with(...)`? The former does not verify the arguments passed to the notifier.
- Is the "notification not called on failure" test present? AI frequently omits this negative assertion, leaving a gap where a buggy implementation that always notifies would still pass.
- Does your AI include a test for the 403 case? If role checking is in the service layer (as `caller_role` parameter), it belongs in this file. If the router handles it via FastAPI middleware, it belongs in `tests/test_job_router.py` instead — and including it here would be testing the wrong layer.

</details>

---

## References

- [pytest Documentation](https://docs.pytest.org/) — Test framework; fixtures, assertions, and the `pytest.raises` context manager
- [pytest-cov](https://pytest-cov.readthedocs.io/) — Coverage plugin; `--cov` and `--cov-report=term-missing` flags used in Activity 1, Step 3
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html) — `MagicMock`, `spec=`, `assert_called_once_with`, and `assert_not_called` used throughout
- [Refactoring to Patterns — Strategy](https://refactoring.com/catalog/replaceConditionalWithStrategy.html) — The specific refactoring applied in Activity 2, Step 3
