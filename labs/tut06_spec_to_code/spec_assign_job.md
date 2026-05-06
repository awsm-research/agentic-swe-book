# Specification: Assign Job to Technician

## Context
Field Repair Tracker REST API. Layered architecture: FastAPI → Service Layer → 
Repository Layer → PostgreSQL. Authentication via JWT middleware already implemented.

## Endpoint
POST /jobs/{job_id}/assign

## Access Control
- Only users with role=manager may call this endpoint
- A 403 response is returned for any other role

## Request Body
{
  "assignee_email": "string"   // email address of the technician
}

## Business Rules
1. The job must exist. Return 404 if not found.
2. The technician must exist and have availability=AVAILABLE. Return 409 if not available.
3. On success: update job.assignee_id, set job.status = 'assigned', persist to database.
4. After a successful assignment, send a push notification to the technician 
   asynchronously (do not await — must not block the HTTP response).

## Response (200 OK)
{
  "job_id": "uuid",
  "assignee_email": "string",
  "status": "assigned"
}

## Error Responses
| Code | Condition |
|------|-----------|
| 400  | Request body missing or malformed |
| 403  | Caller is not a manager |
| 404  | Job not found |
| 409  | Technician not found or not available |

## Constraints
- Use dependency injection for the repository and notification service
- All functions must have type annotations
- Do not use global state
- The notification call must be non-blocking (use asyncio.create_task or BackgroundTasks)
