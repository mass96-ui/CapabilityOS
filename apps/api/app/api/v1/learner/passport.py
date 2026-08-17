from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import LearnerDep, DatabaseDep
from app.schemas.passport import EngineeringPassport
from app.services.passport import EngineeringPassportService


router = APIRouter(
    prefix="/learner/passport",
    tags=["Engineering Passport"],
)


@router.get(
    "",
    response_model=EngineeringPassport,
    summary="Get authenticated learner's Engineering Passport",
)
async def get_passport(
    current_user: LearnerDep,
    db: DatabaseDep,
) -> EngineeringPassport:
    service = EngineeringPassportService(db)

    try:
        return await service.build_passport(
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
