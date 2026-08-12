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
