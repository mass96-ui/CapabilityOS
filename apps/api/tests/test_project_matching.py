from types import SimpleNamespace

from app.services.project_matching import ProjectMatchingService


def requirement(capability_id, level=3, importance=1.0, required=True, rid="r1"):
    return SimpleNamespace(
        id=rid,
        capability_id=capability_id,
        minimum_proficiency_level=level,
        importance=importance,
        required=required,
    )


def capability(capability_id, level):
    return SimpleNamespace(
        capability_id=capability_id,
        proficiency_level=level,
    )


def test_all_required_capabilities_match():
    requirements = [
        requirement("python", level=3, rid="r1"),
        requirement("fastapi", level=2, rid="r2"),
    ]

    capabilities = {
        "python": capability("python", 4),
        "fastapi": capability("fastapi", 2),
    }

    result = ProjectMatchingService.evaluate(
        requirements,
        capabilities,
    )

    assert result.eligible is True
    assert result.match_score == 100.0
    assert len(result.matched) == 2
    assert not result.gaps
    assert not result.missing


def test_required_proficiency_gap_makes_project_ineligible():
    requirements = [
        requirement("python", level=4, rid="r1"),
    ]

    capabilities = {
        "python": capability("python", 2),
    }

    result = ProjectMatchingService.evaluate(
        requirements,
        capabilities,
    )

    assert result.eligible is False
    assert result.gaps[0].gap == 2
    assert result.match_score == 50.0


def test_missing_required_capability_makes_project_ineligible():
    requirements = [
        requirement("python", level=3, rid="r1"),
    ]

    result = ProjectMatchingService.evaluate(
        requirements,
        {},
    )

    assert result.eligible is False
    assert len(result.missing) == 1
    assert result.match_score == 0.0


def test_missing_optional_capability_does_not_block_eligibility():
    requirements = [
        requirement("python", level=3, required=True, rid="r1"),
        requirement("llm", level=2, required=False, rid="r2"),
    ]

    capabilities = {
        "python": capability("python", 3),
    }

    result = ProjectMatchingService.evaluate(
        requirements,
        capabilities,
    )

    assert result.eligible is True
    assert result.match_score == 50.0
    assert len(result.missing) == 1
    assert result.missing[0].required is False
import pytest
from sqlalchemy import select

from app.database.session import AsyncSessionFactory
from app.models.user import User
from app.models.capability import Capability
from app.models.project import Project
from app.models.project_requirement import ProjectRequirement
from app.models.user_capability import UserCapability
from app.services.project_matching import ProjectMatchingService


@pytest.mark.asyncio
async def test_project_matching_with_real_database_records():
    async with AsyncSessionFactory() as session:
        user = User(
            first_name="Matching",
            last_name="Test",
            username="matching_integration_user",
            email="matching.integration@test.local",
            password_hash="test-password-hash",
        )

        capability = Capability(
            name="Python Integration Matching",
            slug="python-matching-integration-unique",
            category="technical",
        )

        session.add_all([user, capability])
        await session.flush()

        project = Project(
            name="Python Integration Project",
            description="Matching integration test",
            status="open",
            project_type="practical",
            owner_id=user.id,
        )

        session.add(project)
        await session.flush()

        requirement = ProjectRequirement(
            project_id=project.id,
            capability_id=capability.id,
            minimum_proficiency_level=3,
            importance=1.0,
            required=True,
        )

        user_capability = UserCapability(
            user_id=user.id,
            capability_id=capability.id,
            proficiency_level=4,
            score=85.0,
            confidence=0.9,
            verified=True,
        )

        session.add_all([requirement, user_capability])
        await session.flush()

        requirements_result = await session.execute(
            select(ProjectRequirement).where(
                ProjectRequirement.project_id == project.id
            )
        )

        user_capabilities_result = await session.execute(
            select(UserCapability).where(
                UserCapability.user_id == user.id
            )
        )

        requirements = requirements_result.scalars().all()
        user_capabilities = {
            item.capability_id: item
            for item in user_capabilities_result.scalars().all()
        }

        result = ProjectMatchingService.evaluate(
            requirements,
            user_capabilities,
        )

        assert result.eligible is True
        assert result.match_score == 100.0
        assert len(result.matched) == 1
        assert not result.gaps
        assert not result.missing
