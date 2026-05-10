## 2.8 Acceptance Criteria

*Acceptance criteria* define the specific conditions that must be satisfied for a user story to be considered done. They bridge requirements and testing: each acceptance criterion should be directly testable.

The most common format is **Gherkin** — a structured natural language syntax used by the Cucumber testing framework ([Wynne & Hellesøy, 2012](https://pragprog.com/titles/hwcuc/the-cucumber-book/)):

```gherkin
Given [some initial context]
When  [an action occurs]
Then  [an observable outcome]
```

**Example — US-03: Assign a task to a team member**

```gherkin
Scenario: Successfully assigning a task
  Given I am logged in as a project manager
  And a task with ID "123" exists in my project
  And a team member "alice@example.com" exists in my project
  When I send POST /tasks/123/assign with body {"assignee": "alice@example.com"}
  Then the response status code is 200
  And the task's assignee field is updated to "alice@example.com"
  And alice receives an email notification within 5 minutes

Scenario: Attempting to assign to a non-member
  Given I am logged in as a project manager
  And a task with ID "123" exists in my project
  When I send POST /tasks/123/assign with body {"assignee": "nonmember@example.com"}
  Then the response status code is 400
  And the response body contains {"error": "User is not a member of this project"}

Scenario: Attempting to assign without permission
  Given I am logged in as a regular user (not a project manager)
  When I send POST /tasks/123/assign with body {"assignee": "alice@example.com"}
  Then the response status code is 403
  And the response body contains {"error": "Insufficient permissions"}
```

Well-written acceptance criteria cover:
- The **happy path** (the successful scenario)
- **Error cases** (invalid input, unauthorised access)
- **Edge cases** (boundary conditions, concurrent operations)

---
