# Tutorial 3 — Sample UML Diagrams

The four UML diagrams produced for the Online Learning Platform scenario in
Tutorial 3 Part 3 (sample answers).

## Use Case Diagram

```mermaid
flowchart LR
    Student(["👤 Student"])
    Instructor(["👤 Instructor"])
    Admin(["👤 Admin"])
    PayGateway(["⚙️ Payment Gateway\n(Stripe)"])
    VideoStorage(["⚙️ Video Storage\n(AWS S3)"])
    NotifSvc(["⚙️ Notification Service\n(SendGrid)"])

    subgraph sys ["Online Learning Platform"]
        UC_BROWSE(["Browse Courses"])
        UC_ENROL(["Enrol in Course"])
        UC_WATCH(["Watch Lecture"])
        UC_QUIZ(["Submit Quiz"])
        UC_PROGRESS(["Track Progress"])
        UC_DISCUSS(["Post Discussion"])
        UC_PAY(["Process Payment"])
        UC_NOTIFY(["Send Notification"])
        UC_GRADE(["Auto-grade Quiz"])
        UC_CREATE(["Create Course"])
        UC_UPLOAD(["Upload Lecture"])
        UC_PUBLISH(["Publish / Unpublish Course"])
        UC_ADD_QUIZ(["Add Quiz to Lecture"])
        UC_ANALYTICS(["View Analytics"])
        UC_MANAGE(["Manage User Accounts"])
        UC_APPROVE(["Approve / Reject Course"])
        UC_REPORT(["Generate Revenue Report"])
    end

    Student --- UC_BROWSE
    Student --- UC_ENROL
    Student --- UC_WATCH
    Student --- UC_QUIZ
    Student --- UC_PROGRESS
    Student --- UC_DISCUSS

    Instructor --- UC_CREATE
    Instructor --- UC_UPLOAD
    Instructor --- UC_PUBLISH
    Instructor --- UC_ADD_QUIZ
    Instructor --- UC_ANALYTICS

    Admin --- UC_MANAGE
    Admin --- UC_APPROVE
    Admin --- UC_REPORT

    UC_ENROL -->|"«include»"| UC_PAY
    UC_ENROL -->|"«include»"| UC_NOTIFY
    UC_QUIZ  -->|"«include»"| UC_GRADE
    UC_GRADE -->|"«include»"| UC_PROGRESS

    UC_PAY    --- PayGateway
    UC_UPLOAD --- VideoStorage
    UC_NOTIFY --- NotifSvc
```

## Class Diagram

```mermaid
classDiagram
    class User {
        +id: UUID
        +email: str
        +password_hash: str
        +name: str
        +created_at: datetime
        +login(email: str, password: str) bool
        +update_profile(data: dict) void
    }
    class Student {
        +preferred_language: str
        +billing_address: str
        +quiz_attempts: int
        +last_active_at: datetime
        +enrol(course_id: UUID) Enrolment
        +submit_quiz(quiz_id: UUID, answers: list) QuizResult
        +watch_lecture(lecture_id: UUID) void
        +get_progress(course_id: UUID) float
    }
    class Course {
        +id: UUID
        +title: str
        +description: str
        +price: float
        +is_published: bool
        +created_at: datetime
        +publish() void
        +unpublish() void
        +get_enrolment_count() int
        +get_completion_rate() float
    }
    class Enrolment {
        +id: UUID
        +enrolled_at: datetime
        +status: Enum
        +progress_percent: float
        +completed_at: datetime
    }
    class Payment {
        +id: UUID
        +amount: float
        +status: Enum
    }

    User <|-- Student : inheritance
    Student "1" --> "0..*" Enrolment : has
    Course "1" --> "0..*" Enrolment : receives
    Enrolment "1" *-- "1" Payment : composition
```

(Truncated — see `tutorial_3.md` for the full answer with Instructor, Admin,
Lecture, Quiz classes.)

## Sequence Diagram — Enrol in Course

See the full Mermaid in `tutorial_3.md` Part 3 sample answer.

## Component Diagram

See the full Mermaid in `tutorial_3.md` Part 3 sample answer.
