# CapabilityOS Project Progress

> Last Updated: 2026-08-09
> Status: ACTIVE
> Project Type: Enterprise AI Platform
> Architecture: Clean Architecture + Monorepo

---

# 1. Project Vision

CapabilityOS is an AI-powered industry experience platform designed to bridge the gap between learning and real-world software engineering.

The platform is not intended to be another certificate or assessment platform.

CapabilityOS is designed to understand:

* What a learner knows
* What a learner can actually do
* Which capabilities they have demonstrated
* Their current capability level
* Their practical project performance
* Their readiness for real-world industry work
* Which real-world opportunities match their capabilities

Long-term vision:

```text
Learning
   ↓
Assessment
   ↓
Evidence
   ↓
Capability Scoring
   ↓
Capability Evaluation
   ↓
User Capability Profile
   ↓
Practical Projects
   ↓
Performance Evidence
   ↓
Industry Readiness
   ↓
Opportunity Matching
```

---

# 2. Engineering Standards

* Production Ready
* Clean Architecture
* SOLID
* DRY
* KISS
* OWASP
* REST API
* Type Safe
* Fully Tested
* Fully Documented
* Scalable Architecture
* Explicit Domain Boundaries
* Evidence-Based Capability Evaluation

---

# 3. Technology Stack

## Frontend

* Next.js
* TypeScript
* TailwindCSS

## Admin

* Next.js
* TypeScript

## Backend

* FastAPI
* SQLAlchemy
* Alembic
* PostgreSQL

## Development Database

* SQLite currently used for local development/testing

## Package Management

* pnpm
* Python virtual environment

## Monorepo

* Turborepo

## DevOps

* Docker
* Docker Compose
* GitHub Actions

---

# 4. Monorepo Architecture

```text
CapabilityOS/
│
├── apps/
│   ├── web/
│   ├── admin/
│   └── api/
│
├── PROJECT_PROGRESS.md
├── README.md
├── docker-compose.yml
└── ...
```

Backend:

```text
apps/api/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │
│   ├── core/
│   ├── database/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   └── utils/
│
├── requirements.txt
└── ...
```

---

# 5. Milestone 1 — Repository Foundation

Status: ✅ COMPLETE

Completed:

* [x] Monorepo
* [x] Docker configuration
* [x] Docker Compose
* [x] GitHub Actions
* [x] README
* [x] Environment templates
* [x] Workspace configuration
* [x] Build configuration
* [x] Lint configuration
* [x] Formatting configuration

---

# 6. Milestone 2 — Backend Foundation

Status: ✅ COMPLETE

## Core

* [x] Configuration
* [x] Dependencies
* [x] Exceptions
* [x] Logging
* [x] Security foundation

## Database

* [x] SQLAlchemy Base
* [x] Async database session
* [x] Database initialization
* [x] Database verification

## API

* [x] FastAPI application
* [x] Health endpoint
* [x] Readiness endpoint
* [x] Liveness endpoint

---

# 7. Milestone 3 — User & Capability Foundation

Status: ✅ COMPLETE

## Models

* [x] User
* [x] Capability
* [x] UserCapability

## Repositories

* [x] User repository
* [x] Capability repository
* [x] UserCapability repository

## Services

* [x] User service
* [x] Capability service
* [x] UserCapability service

---

# 8. Milestone 4 — Assessment Engine

Status: ✅ COMPLETE

## Models

* [x] Assessment
* [x] AssessmentAttempt
* [x] AssessmentQuestion
* [x] AssessmentAnswer
* [x] AssessmentEvidence

## Repositories

* [x] Assessment repository
* [x] AssessmentAttempt repository
* [x] AssessmentQuestion repository
* [x] AssessmentAnswer repository
* [x] AssessmentEvidence repository

## Services

* [x] AssessmentService
* [x] AssessmentQuestionService
* [x] AssessmentAnswerService
* [x] AssessmentAttemptService

## Assessment lifecycle

```text
Assessment
    ↓
Questions
    ↓
Attempt
    ↓
Answer Submission
    ↓
Answer Evaluation
    ↓
Attempt Statistics
    ↓
Attempt Submission
    ↓
Assessment Result
```

---

# 9. Assessment Engine Verification

Status: ✅ VERIFIED

Previously verified assessment attempt:

```text
Attempt ID:
8fea5f19-1bab-4d81-891b-a56a5b4ac077
```

Result:

```text
Status: submitted
Questions: 5
Answered: 5
Correct: 4
Score: 4.0
Maximum Score: 5.0
Percentage: 80.0%
```

Verified endpoints include:

```text
POST
/api/v1/assessment-attempts/{attempt_id}/submit
```

and:

```text
GET
/api/v1/assessment-attempts/{attempt_id}/result
```

---

# 10. Milestone 5 — Capability Intelligence

Status: 🟢 IMPLEMENTED — INTEGRATION TESTING NEXT

Capability Intelligence is now implemented as the first major intelligence subsystem.

The architecture is:

```text
Assessment Answer
        ↓
Assessment Evidence
        ↓
Capability Scoring
        ↓
Capability Score Result
        ↓
Capability Evaluation
        ↓
UserCapability
        ↓
CapabilityScoreHistory
```

This means CapabilityOS now has a complete path from assessment evidence to a persisted user capability state.

---

# 11. Assessment Evidence

Status: ✅ COMPLETE

Model:

```text
AssessmentEvidence
```

Database table:

```text
assessment_evidence
```

Evidence contains:

* attempt_id
* answer_id
* user_id
* capability_id
* skill_dimension
* evidence_type
* evidence_score
* evidence_weight
* confidence
* evaluator_type
* evaluation_reason
* metadata_json
* created_at
* updated_at

Current MVP evidence rule:

```text
Correct answer
    ↓
evidence_score = 100

Incorrect answer
    ↓
evidence_score = 0
```

Current default:

```text
evidence_weight = question.points
confidence = 1.0
evidence_type = "assessment"
evaluator_type = "rule_based"
```

---

# 12. Assessment Answer → Evidence

Status: ✅ IMPLEMENTED

`AssessmentAnswerService` now performs:

```text
Submit Answer
     ↓
Validate Attempt
     ↓
Validate Question
     ↓
Evaluate Answer
     ↓
Create AssessmentAnswer
     ↓
Create AssessmentEvidence
     ↓
Update Attempt Statistics
```

The assessment answer is therefore no longer isolated from the capability system.

Every evaluated answer can contribute measurable evidence toward the associated capability.

---

# 13. Capability Scoring Service

Status: ✅ COMPLETE

Service:

```text
CapabilityScoringService
```

Result model:

```text
CapabilityScoreResult
```

Current structure:

```text
CapabilityScoreResult(
    user_id,
    capability_id,
    score,
    proficiency,
    proficiency_level,
    confidence,
    evidence_count
)
```

Verified constructor:

```text
(user_id: str,
 capability_id: str,
 score: float,
 proficiency: str,
 proficiency_level: int,
 confidence: float,
 evidence_count: int)
```

The integer proficiency level is now explicitly available.

Current mapping:

```text
emerging   → 1
developing → 2
proficient → 3
advanced   → 4
```

---

# 14. Capability Evaluation Service

Status: ✅ COMPLETE

Service:

```text
CapabilityEvaluationService
```

Responsibility:

```text
Assessment Evidence
        ↓
CapabilityScoringService
        ↓
CapabilityScoreResult
        ↓
Compare Previous Capability
        ↓
Update UserCapability
        ↓
Create CapabilityScoreHistory
```

The service currently:

1. Calculates capability score.
2. Retrieves previous UserCapability.
3. Calculates score delta.
4. Updates current UserCapability.
5. Records historical capability score.
6. Returns CapabilityScoreResult.

---

# 15. UserCapability Persistence

Status: ✅ COMPLETE

Current capability state is persisted through:

```text
UserCapabilityRepository
```

Stored information includes:

* user_id
* capability_id
* proficiency_level
* score
* confidence
* verified
* last_assessed_at

This represents the user's **current capability state**.

---

# 16. Capability Score History

Status: ✅ COMPLETE

Historical evaluations are stored in:

```text
capability_score_history
```

History contains:

* user_id
* capability_id
* score
* proficiency
* confidence
* previous_score
* score_delta
* source
* attempt_id
* evidence_id
* reason
* metadata_json

This allows CapabilityOS to track capability progression over time.

Example:

```text
Evaluation 1
Score: 52
       ↓
Evaluation 2
Score: 67
       ↓
Evaluation 3
Score: 81
       ↓
Evaluation 4
Score: 88
```

---

# 17. Current Capability Intelligence Pipeline

Status: ✅ IMPLEMENTED

The current backend architecture is:

```text
                 Assessment
                     ↓
              Assessment Attempt
                     ↓
                Answer Submit
                     ↓
              Answer Evaluation
                     ↓
           AssessmentEvidence
                     ↓
          CapabilityScoringService
                     ↓
           CapabilityScoreResult
                     ↓
        CapabilityEvaluationService
                     ↓
              ┌──────┴──────┐
              ↓             ↓
       UserCapability   ScoreHistory
              ↓             ↓
        Current State    Historical State
```

This is the core capability intelligence foundation.

---

# 18. Verified Database Tables

Status: ✅ VERIFIED

Current database tables:

```text
assessment_answers
assessment_attempts
assessment_evidence
assessment_questions
assessments
capabilities
capability_score_history
user_capabilities
users
```

SQLAlchemy metadata verification also confirmed:

```text
users
capabilities
user_capabilities
assessments
assessment_attempts
assessment_questions
assessment_answers
assessment_evidence
capability_score_history
```

---

# 19. Verified Service Imports

Status: ✅ VERIFIED

Capability scoring:

```text
CAPABILITY SCORING: OK
```

Capability evaluation:

```text
CAPABILITY EVALUATION: OK
```

Assessment answer:

```text
ASSESSMENT ANSWER: OK
```

Assessment attempt:

```text
ASSESSMENT ATTEMPT: OK
```

Full pipeline:

```text
FULL CAPABILITY PIPELINE: OK
```

Therefore all major service modules currently import successfully.

---

# 20. Current Architecture Principle

CapabilityOS must distinguish:

```text
Assessment Score
```

from:

```text
Capability
```

An assessment score is only one piece of evidence.

The architecture therefore follows:

```text
Assessment
    ↓
Evidence
    ↓
Scoring
    ↓
Evaluation
    ↓
Capability
```

Long-term:

```text
Assessment Evidence
        +
Coding Evidence
        +
Project Evidence
        +
Task Evidence
        +
Mentor Evidence
        +
Industry Evidence
        ↓
Capability Intelligence
```

---

# 21. Current MVP Evidence Model

For the current MCQ assessment MVP:

```text
Correct
    ↓
100 evidence score

Incorrect
    ↓
0 evidence score
```

Question points determine evidence weight:

```text
Question points
       ↓
Evidence weight
```

Example:

```text
Question 1
Correct
2 points
    ↓
100 × 2

Question 2
Incorrect
1 point
    ↓
0 × 1

Question 3
Correct
3 points
    ↓
100 × 3
```

This is intentionally simple for the MVP.

Future evidence sources will use richer scoring models.

---

# 22. Current Verification Gap

Status: 🟡 NEXT TEST

The service imports are verified.

Database tables are verified.

Model registration is verified.

The remaining important validation is a **real end-to-end capability evaluation test**.

Required flow:

```text
Create/Use User
      ↓
Create/Use Capability
      ↓
Create Assessment
      ↓
Create Questions
      ↓
Create Attempt
      ↓
Submit Answers
      ↓
Generate Assessment Evidence
      ↓
Submit Attempt
      ↓
Run Capability Evaluation
      ↓
Verify UserCapability
      ↓
Verify CapabilityScoreHistory
```

The next test must confirm that the complete pipeline works with real database records.

---

# 23. Immediate Next Task

Status: 🔵 NEXT

## End-to-End Capability Pipeline Test

The next development task is NOT another service rewrite.

The next task is integration validation.

Verify:

```text
Assessment Answer
        ↓
Assessment Evidence
        ↓
Capability Scoring
        ↓
Capability Evaluation
        ↓
UserCapability
        ↓
CapabilityScoreHistory
```

The test should verify:

* Evidence is created.
* Evidence has the correct capability.
* Evidence belongs to the correct user.
* Evidence score is correct.
* Capability score is calculated.
* Proficiency is calculated.
* Proficiency level is calculated.
* UserCapability is created/updated.
* Previous score is detected.
* Score delta is calculated.
* CapabilityScoreHistory is created.
* Attempt ID is preserved in history.

---

# 24. Milestone 6 — Practical Projects

Status: 🔵 PLANNED

After capability intelligence is verified, build practical project intelligence.

Target:

```text
Company Requirement
        ↓
Project Definition
        ↓
Required Capabilities
        ↓
Capability Matching
        ↓
Candidate Selection
        ↓
Team Formation
        ↓
Real Project
        ↓
Task Performance
        ↓
Performance Evidence
```

Planned:

* [ ] Project model
* [ ] Project requirements
* [ ] Project capabilities
* [ ] Project tasks
* [ ] Team assignment
* [ ] Task assignment
* [ ] Submission
* [ ] Code evaluation
* [ ] Mentor review
* [ ] Project performance
* [ ] Industry feedback

---

# 25. Milestone 7 — Advanced Evidence Engine

Status: 🔵 PLANNED

Future evidence types:

```text
Assessment
Coding Task
GitHub Project
Project Performance
Mentor Review
Manager Review
Industry Feedback
AI Evaluation
```

Target:

```text
                    Evidence
                       │
       ┌───────────────┼───────────────┐
       ↓               ↓               ↓
   Assessment       Projects        Human Review
       ↓               ↓               ↓
       └───────────────┼───────────────┘
                       ↓
              Capability Intelligence
```

---

# 26. Milestone 8 — AI Engine

Status: 🔵 PLANNED

AI development comes AFTER the capability foundation is stable.

Planned:

* [ ] AI assessment generation
* [ ] Adaptive assessments
* [ ] Capability inference
* [ ] Capability gap analysis
* [ ] Personalized learning recommendations
* [ ] Project recommendations
* [ ] Opportunity matching
* [ ] RAG
* [ ] Web Search Agents
* [ ] LangGraph
* [ ] MCP
* [ ] Multi-agent workflows

AI should consume structured capability intelligence.

It should not replace the domain model.

---

# 27. Milestone 9 — Industry Matching

Status: 🔵 PLANNED

Long-term target:

```text
Startup Problem
       ↓
Required Capabilities
       ↓
CapabilityOS Intelligence
       ↓
Candidate Ranking
       ↓
Team Recommendation
       ↓
Real Project
       ↓
Performance
       ↓
Payment / Recognition
```

The platform should ultimately answer:

> Who can actually solve this problem?

rather than:

> Who completed this course?

---

# 28. Milestone 10 — Authentication & Security

Status: 🔵 PLANNED

* [ ] Authentication
* [ ] JWT
* [ ] Refresh tokens
* [ ] Password hashing
* [ ] RBAC
* [ ] Authentication middleware
* [ ] Request ID
* [ ] Security middleware
* [ ] Permission system

---

# 29. Milestone 11 — Notifications

Status: 🔵 PLANNED

* [ ] Notification model
* [ ] Email notifications
* [ ] In-app notifications
* [ ] Assessment notifications
* [ ] Project notifications
* [ ] Opportunity notifications

---

# 30. Milestone 12 — Deployment

Status: 🔵 PLANNED

* [ ] PostgreSQL production configuration
* [ ] Docker production setup
* [ ] CI/CD
* [ ] Environment management
* [ ] Monitoring
* [ ] Logging
* [ ] Error tracking
* [ ] Backup strategy
* [ ] Production deployment

---

# 31. Overall Project Status

```text
Repository Foundation          ✅ COMPLETE
Backend Foundation             ✅ COMPLETE
User Foundation                ✅ COMPLETE
Capability Foundation          ✅ COMPLETE
Assessment Engine              ✅ COMPLETE
Assessment Submission          ✅ COMPLETE
Assessment Result              ✅ COMPLETE
Assessment Evidence            ✅ COMPLETE
Capability Scoring             ✅ COMPLETE
Capability Evaluation          ✅ COMPLETE
UserCapability Persistence     ✅ COMPLETE
Capability Score History       ✅ COMPLETE
End-to-End Pipeline Test       🟡 NEXT
Practical Projects             🔵 PLANNED
Advanced Evidence              🔵 PLANNED
AI Engine                      🔵 PLANNED
Industry Matching              🔵 PLANNED
Authentication/RBAC            🔵 PLANNED
Notifications                  🔵 PLANNED
Deployment                     🔵 PLANNED
```

---

# 32. Current System Architecture

```text
                         CapabilityOS
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
      Learning            Assessment          Projects
                              │                   │
                              ▼                   │
                       Assessment Attempt        │
                              │                   │
                              ▼                   │
                         Answer Submit            │
                              │                   │
                              ▼                   │
                    Assessment Evidence          │
                              │                   │
                              ▼                   │
                   Capability Scoring             │
                              │                   │
                              ▼                   │
                   Capability Evaluation          │
                              │                   │
                 ┌────────────┴────────────┐      │
                 ▼                         ▼      │
          UserCapability          ScoreHistory    │
                 │                         │       │
                 └────────────┬────────────┘       │
                              ▼                    │
                    Capability Intelligence        │
                              │                    │
                              └─────────┬──────────┘
                                        ▼
                              Industry Readiness
                                        │
                                        ▼
                                AI Opportunity
                                   Matching
```

---

# 33. Development Rules

* Never regenerate completed files.
* Update `PROJECT_PROGRESS.md` after meaningful architectural milestones.
* Do not rebuild working services unnecessarily.
* Validate every new service with import checks.
* Validate database metadata after model changes.
* Validate real database behavior after integration changes.
* Preserve clean architecture boundaries.
* Keep repositories responsible for persistence.
* Keep services responsible for business logic.
* Keep schemas responsible for API data contracts.
* Keep models responsible for persistence structure.
* Do not treat one assessment score as permanent capability truth.
* Capability must remain evidence-driven.
* AI should be added after the capability foundation is stable.
* Every new subsystem should follow:

```text
Model
  ↓
Repository
  ↓
Service
  ↓
Schema
  ↓
API
  ↓
Test
```

---

# 34. Immediate Development Roadmap

```text
CURRENT
   │
   ▼
End-to-End Capability Pipeline Test
   │
   ▼
Fix Integration Issues
   │
   ▼
Capability API Verification
   │
   ▼
Capability Dashboard
   │
   ▼
Project Intelligence
   │
   ▼
Project Evidence
   │
   ▼
Advanced Capability Intelligence
   │
   ▼
RAG
   │
   ▼
LangGraph
   │
   ▼
MCP
   │
   ▼
Industry Opportunity Matching
```

---

# 35. Project Philosophy

CapabilityOS is not:

```text
Course
   ↓
Certificate
```

It is:

```text
Learn
   ↓
Demonstrate
   ↓
Measure
   ↓
Evaluate
   ↓
Build
   ↓
Perform
   ↓
Prove
   ↓
Match
   ↓
Work
```

The long-term intelligence of CapabilityOS comes from accumulated evidence of what a person can actually do.

---

# 36. Current Development Position

```text
              YOU ARE HERE
                    ↓
Assessment → Evidence → Scoring → Evaluation
                                      │
                                      ▼
                               User Capability
                                      │
                                      ▼
                         🔵 END-TO-END TEST
                                      │
                                      ▼
                              Project System
```

The **Capability Intelligence foundation is now implemented**.

The next objective is to prove that it works end-to-end with actual records before adding another major subsystem.
