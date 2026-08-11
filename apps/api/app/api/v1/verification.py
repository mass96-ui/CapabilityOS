from fastapi import APIRouter

router = APIRouter(
    prefix="/verification",
    tags=["Email Verification"],
)


@router.get(
    "/health",
    summary="Check email verification service",
)
async def verification_health():
    return {
        "status": "ok",
        "service": "email-verification",
    }