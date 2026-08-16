from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import LearnerDep, DatabaseDep
from app.schemas.learner.profile import (
    LearnerProfileCreate,
    LearnerProfileResponse,
    LearnerProfileUpdate,
)
from app.services.learner.profile import LearnerProfileService


router = APIRouter(
    prefix="/learner/profile",
    tags=["Learner Profile"],
)


# ==========================================================
# GET CURRENT LEARNER PROFILE
# ==========================================================

@router.get(
    "",
    response_model=LearnerProfileResponse,
    summary="Get current learner profile",
)
async def get_my_profile(
    current_user: LearnerDep,
    db: DatabaseDep,
) -> LearnerProfileResponse:

    service = LearnerProfileService(db)

    profile = await service.get_by_user_id(
        user_id=current_user.id,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile does not exist.",
        )

    return LearnerProfileResponse.model_validate(profile)


# ==========================================================
# CREATE CURRENT LEARNER PROFILE
# ==========================================================

@router.post(
    "",
    response_model=LearnerProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create current learner profile",
)
async def create_my_profile(
    request: LearnerProfileCreate,
    current_user: LearnerDep,
    db: DatabaseDep,
) -> LearnerProfileResponse:

    if str(request.user_id) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot create a profile for another user.",
        )

    service = LearnerProfileService(db)

    try:
        profile = await service.create_profile(
            user_id=current_user.id,
            display_name=request.display_name,
            headline=request.headline,
            bio=request.bio,
            location=request.location,
            profile_image_url=request.profile_image_url,
        )

        await db.commit()

        return LearnerProfileResponse.model_validate(profile)

    except ValueError as exc:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


# ==========================================================
# UPDATE CURRENT LEARNER PROFILE
# ==========================================================

@router.patch(
    "",
    response_model=LearnerProfileResponse,
    summary="Update current learner profile",
)
async def update_my_profile(
    request: LearnerProfileUpdate,
    current_user: LearnerDep,
    db: DatabaseDep,
) -> LearnerProfileResponse:

    service = LearnerProfileService(db)

    profile = await service.update_profile(
        user_id=current_user.id,
        **request.model_dump(exclude_unset=True),
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile does not exist.",
        )

    await db.commit()

    return LearnerProfileResponse.model_validate(profile)