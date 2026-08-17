from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUserDep, LearnerDep, ManagerDep
from app.database.session import get_session
from app.models.project import Project
from app.models.project_requirement import ProjectRequirement
from app.models.user import User
from app.models.user_capability import UserCapability
from app.repositories.capability import CapabilityRepository
from app.schemas.project_matching import (
    CandidateMatchResponse,
    ManagerMatchResponse,
    ProjectMatchResponse,
    RequirementMatchResponse,
)
from app.services.project_matching import ProjectMatchingService

router = APIRouter(
    prefix="/projects",
    tags=["Project Matching"],
)


async def _build_capability_name_map(
    requirement_capability_ids: list[str],
    capability_repo: CapabilityRepository,
) -> dict[str, str]:
    capability_names: dict[str, str] = {}

    for capability_id in requirement_capability_ids:
        capability = await capability_repo.get_by_id(
            capability_id
        )
        if capability is not None:
            capability_names[capability_id] = capability.name

    return capability_names


@router.get("/{project_id}/match", response_model=ProjectMatchResponse)
async def match_project(
    project_id: str,
    current_user: LearnerDep,
    session: AsyncSession = Depends(get_session),
):
    project_result = await session.execute(
        select(Project).where(Project.id == project_id)
    )
    project = project_result.scalar_one_or_none()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    requirements_result = await session.execute(
        select(ProjectRequirement).where(
            ProjectRequirement.project_id == project_id
        )
    )
    requirements = requirements_result.scalars().all()

    capabilities_result = await session.execute(
        select(UserCapability).where(
            UserCapability.user_id == current_user.id
        )
    )

    user_capabilities = {
        item.capability_id: item
        for item in capabilities_result.scalars().all()
    }

    capability_repo = CapabilityRepository(session)
    requirement_capability_ids = [
        req.capability_id for req in requirements
    ]
    capability_names = await _build_capability_name_map(
        requirement_capability_ids,
        capability_repo,
    )

    result = ProjectMatchingService.evaluate(
        requirements,
        user_capabilities,
        capability_names=capability_names,
    )

    return {
        "project_id": project.id,
        "user_id": current_user.id,
        **asdict(result),
    }


@router.get("/{project_id}/matches", response_model=ManagerMatchResponse)
async def match_project_for_all_learners(
    project_id: str,
    current_user: ManagerDep,
    session: AsyncSession = Depends(get_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    project_result = await session.execute(
        select(Project).where(Project.id == project_id)
    )
    project = project_result.scalar_one_or_none()

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    is_admin = (
        current_user.is_superuser
        or current_user.role == "admin"
    )

    if not is_admin and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to view matches for this project.",
        )

    requirements_result = await session.execute(
        select(ProjectRequirement).where(
            ProjectRequirement.project_id == project_id
        )
    )
    requirements = requirements_result.scalars().all()

    requirement_capability_ids = [
        req.capability_id for req in requirements
    ]

    capability_repo = CapabilityRepository(session)
    capability_names = await _build_capability_name_map(
        requirement_capability_ids,
        capability_repo,
    )

    user_capabilities_result = await session.execute(
        select(UserCapability).where(
            UserCapability.capability_id.in_(requirement_capability_ids)
        )
    )
    all_capabilities = user_capabilities_result.scalars().all()

    capabilities_by_user: dict[str, list] = {}
    for cap in all_capabilities:
        capabilities_by_user.setdefault(
            cap.user_id, []
        ).append(cap)

    users_result = await session.execute(
        select(User).where(
            User.is_active == True,
        )
    )
    users = users_result.scalars().all()

    raw_matches = []

    for user in users:
        user_caps = {
            item.capability_id: item
            for item in capabilities_by_user.get(
                user.id, []
            )
        }

        result = ProjectMatchingService.evaluate(
            requirements,
            user_caps,
            capability_names=capability_names,
        )

        raw_matches.append({
            "user_id": user.id,
            "user_email": user.email,
            "user_name": (
                f"{user.first_name} {user.last_name}"
            ),
            "result": result,
        })

    raw_matches.sort(
        key=lambda m: (
            m["result"].eligible,
            m["result"].match_score,
        ),
        reverse=True,
    )

    total_candidates = len(raw_matches)
    eligible_count = sum(
        1 for m in raw_matches if m["result"].eligible
    )

    offset = (page - 1) * page_size
    page_matches = raw_matches[offset:offset + page_size]
    total_pages = (
        (total_candidates + page_size - 1) // page_size
        if total_candidates
        else 0
    )

    matches = [
        CandidateMatchResponse(
            user_id=m["user_id"],
            user_email=m["user_email"],
            user_name=m["user_name"],
            eligible=m["result"].eligible,
            match_score=m["result"].match_score,
            coverage_ratio=m["result"].coverage_ratio,
            matched=[
                RequirementMatchResponse(
                    **asdict(r)
                )
                for r in m["result"].matched
            ],
            gaps=[
                RequirementMatchResponse(
                    **asdict(r)
                )
                for r in m["result"].gaps
            ],
            missing=[
                RequirementMatchResponse(
                    **asdict(r)
                )
                for r in m["result"].missing
            ],
        )
        for m in page_matches
    ]

    return ManagerMatchResponse(
        project_id=project.id,
        total_candidates=total_candidates,
        eligible_count=eligible_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        matches=matches,
    )
