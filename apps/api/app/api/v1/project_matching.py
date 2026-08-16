from dataclasses import asdict

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.core.dependencies import CurrentUserDep, LearnerDep
from app.database.session import AsyncSessionFactory
from app.models.project import Project
from app.models.project_requirement import ProjectRequirement
from app.models.user_capability import UserCapability
from app.services.project_matching import ProjectMatchingService

router = APIRouter(
    prefix="/projects",
    tags=["Project Matching"],
)


@router.get("/{project_id}/match")
async def match_project(
    project_id: str,
    current_user: LearnerDep,
):
    async with AsyncSessionFactory() as session:
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

        result = ProjectMatchingService.evaluate(
            requirements,
            user_capabilities,
        )

        return {
            "project_id": project.id,
            "user_id": current_user.id,
            **asdict(result),
        }
