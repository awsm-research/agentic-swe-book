## 2.6 Prioritisation: The MoSCoW Framework

Once user stories are written, the team must decide which to build first. The **MoSCoW framework** ([Clegg & Barker, 1994](https://www.dsdm.org/)) provides a shared vocabulary for this:

| Category | Meaning | Guideline |
|---|---|---|
| **M**ust Have | Non-negotiable; the system cannot launch without these | ~60% of effort |
| **S**hould Have | Important but not vital; workarounds exist if omitted | ~20% of effort |
| **C**ould Have | Nice to have; included only if time permits | ~20% of effort |
| **W**on't Have | Explicitly excluded from this release | Documented, not built |

The "Won't Have" category is often the most valuable: it makes explicit what is being deliberately deferred, turning unspoken assumptions into shared agreements.

**Example — a task management application:**

| Feature | MoSCoW |
|---|---|
| Create, read, update, delete tasks | Must Have |
| Assign tasks to team members | Must Have |
| Email notifications on task assignment | Should Have |
| Drag-and-drop task reordering | Could Have |
| Integration with Slack | Won't Have (this release) |

---
