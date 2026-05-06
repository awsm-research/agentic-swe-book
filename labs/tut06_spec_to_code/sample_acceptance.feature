Scenario: Successfully assigning a job to an available technician
  Given I am authenticated as a Service Manager
  And a job with ID "job-42" exists with status "unassigned"
  And a technician "alex@fieldco.com" exists and is available
  When I send POST /jobs/job-42/assign with body {"assignee": "alex@fieldco.com"}
  Then the response status is 200
  And the job's assignee is updated to "alex@fieldco.com"
  And the job status changes to "assigned"
  And alex receives a push notification within 10 seconds

Scenario: Attempting to assign a job to an unavailable technician
  Given I am authenticated as a Service Manager
  And a job with ID "job-42" exists
  And technician "alex@fieldco.com" has status "on_leave"
  When I send POST /jobs/job-42/assign with body {"assignee": "alex@fieldco.com"}
  Then the response status is 409
  And the response body contains {"error": "Technician is not available"}

Scenario: Field technician attempts to assign a job
  Given I am authenticated as a Field Technician (not a manager)
  When I send POST /jobs/job-42/assign with body {"assignee": "sam@fieldco.com"}
  Then the response status is 403
  And the response body contains {"error": "Insufficient permissions"}
