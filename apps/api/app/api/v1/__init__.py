from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.verification import router as email_verification_router
from app.api.v1.learner.profile import (
    router as learner_profile_router,
)

router = APIRouter()

# ============================================================
# Authentication
# ============================================================

router.include_router(
    auth_router,
)

# ============================================================
# Email Verification
# ============================================================

router.include_router(
    email_verification_router,
)

# ============================================================
# Learner
# ============================================================

router.include_router(
    learner_profile_router,
)