## 2.5 Epics, User Stories, and Work Items

In Agile teams, requirements are typically captured as a hierarchy of work items:

```
Epic
 └── Feature / Capability
      └── User Story
           └── Task (implementation subtask)
```

### 2.5.1 Epics

An *epic* is a large body of work that can be broken down into smaller stories. Epics represent significant chunks of functionality — typically too large to complete in a single sprint.

**Example epics for a task management system:**

- User Authentication and Authorisation
- Task Lifecycle Management (create, assign, update, complete)
- Notifications and Alerts
- Reporting and Analytics

### 2.5.2 User Stories

Each epic decomposes into user stories — small, independently deliverable increments of value.

**Epic: Task Lifecycle Management**

| ID | User Story |
|---|---|
| US-01 | As a user, I want to create a task with a title and description so that I can record work that needs to be done. |
| US-02 | As a user, I want to assign a due date to a task so that I can track deadlines. |
| US-03 | As a project manager, I want to assign a task to a team member so that responsibilities are clear. |
| US-04 | As a user, I want to mark a task as complete so that the team can see progress. |
| US-05 | As a user, I want to add comments to a task so that I can communicate context without leaving the tool. |

### 2.5.3 Story Points

*Story points* are a unit of measure for estimating the relative effort or complexity of user stories. They are intentionally abstract — they do not map directly to hours or days — encouraging teams to think about relative complexity rather than precise time estimates.

Teams typically use a modified Fibonacci sequence: **1, 2, 3, 5, 8, 13, 21**. The increasing gaps reflect growing uncertainty in estimating large, complex work.

**Planning Poker** is a common estimation technique ([Grenning, 2002](https://wingman-sw.com/articles/planning-poker)): each team member privately selects a card with their estimate; all cards are revealed simultaneously; significant discrepancies prompt discussion until the team reaches consensus.

Story points enable **velocity tracking** — the total points completed per sprint gives the team's *velocity*, which predicts future throughput and informs release planning.

### 2.5.4 Tasks

Each user story is implemented through one or more *tasks* — specific technical actions. Tasks are not user-visible; they are engineering sub-steps.

**Example tasks for US-03 (assign a task to a team member):**

- Design the `POST /tasks/{id}/assign` API endpoint
- Implement the assignment logic and database update
- Write unit tests for the assignment service
- Write integration tests for the assignment endpoint
- Update API documentation

---
