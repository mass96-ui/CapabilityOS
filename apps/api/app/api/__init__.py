from fastapi import APIRouter

from app.api.v1.learner.profile import (
    router as learner_profile_router,
)

from app.api.v1.assessment_attempts import (
    router as assessment_attempts_router,
)

from app.api.v1.assessment_questions import (
    router as assessment_questions_router,
)

from app.api.v1.health import (
    router as health_router,
)

from app.api.v1.capabilities import (
    router as capabilities_router,
)

from app.api.v1.user_capabilities import (
    router as user_capabilities_router,
)

from app.api.v1.assessments import (
    router as assessments_router,
)

from app.api.v1.assessment_answers import (
    router as assessment_answers_router,
)

from app.api.v1.capability_score_history import (
    router as capability_score_history_router,
)

from app.api.v1.projects import (
    router as projects_router,
)
from app.api.v1.project_matching import (
    router as project_matching_router,
)


api_router = APIRouter()


# ==========================================================
# HEALTH
# ==========================================================

api_router.include_router(
    health_router,
    prefix="/v1",
    tags=["Health"],
)


# ==========================================================
# CAPABILITIES
# ==========================================================

api_router.include_router(
    capabilities_router,
    prefix="/v1/capabilities",
    tags=["Capabilities"],
)


# ==========================================================
# USER CAPABILITIES
# ==========================================================

api_router.include_router(
    user_capabilities_router,
    prefix="/v1/users",
    tags=["User Capabilities"],
)


# ==========================================================
# ASSESSMENTS
# ==========================================================

api_router.include_router(
    assessments_router,
    prefix="/v1/assessments",
    tags=["Assessments"],
)


# ==========================================================
# ASSESSMENT ATTEMPTS
# ==========================================================

api_router.include_router(
    assessment_attempts_router,
    prefix="/v1/assessment-attempts",
    tags=["Assessment Attempts"],
)


# ==========================================================
# ASSESSMENT QUESTIONS
# ==========================================================

api_router.include_router(
    assessment_questions_router,
    prefix="/v1/assessment-questions",
    tags=["Assessment Questions"],
)


# ==========================================================
# ASSESSMENT ANSWERS
# ==========================================================

api_router.include_router(
    assessment_answers_router,
    prefix="/v1/assessment-answers",
    tags=["Assessment Answers"],
)


# ==========================================================
# CAPABILITY SCORE HISTORY
# ==========================================================

api_router.include_router(
    capability_score_history_router,
    prefix="/v1/capability-score-history",
    tags=["Capability Score History"],
)


# ==========================================================
# PROJECT MANAGEMENT
# ==========================================================

api_router.include_router(
    projects_router,
    prefix="/v1/projects",
    tags=["Projects"],
)

api_router.include_router(
    project_matching_router,
    prefix="/v1",
    tags=["Project Matching"],
)


# ==========================================================
# LEARNER PROFILE
# ==========================================================

api_router.include_router(
    learner_profile_router,
    prefix="/v1",
)